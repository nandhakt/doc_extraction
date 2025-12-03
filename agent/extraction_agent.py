"""
LangGraph-based Document Extraction Agent with Human-in-the-Loop feedback support.
"""

import json
from typing import TypedDict, Annotated, Literal, Optional
from operator import add

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from config import OPENAI_API_KEY, OPENAI_MODEL


class ExtractionState(TypedDict):
    """State for the extraction workflow."""
    document_text: str
    json_schema: dict
    extracted_data: Optional[dict]
    confidence_scores: Optional[dict]
    human_feedback: Optional[str]
    iteration: int
    max_iterations: int
    status: str
    messages: Annotated[list, add]


def create_extraction_prompt(document_text: str, schema: dict, feedback: Optional[str] = None) -> str:
    """Create the extraction prompt with optional feedback."""
    
    schema_str = json.dumps(schema, indent=2)
    
    base_prompt = f"""You are an expert document data extraction agent. Extract the required fields from the document according to the provided JSON schema.

## JSON Schema (defines required fields):
```json
{schema_str}
```

## Document Content:
```
{document_text}
```

## Instructions:
1. Extract ALL fields defined in the schema from the document
2. For each field, provide:
   - The extracted value (or null if not found)
   - A confidence score (0.0 to 1.0)
3. Be precise and extract exact values as they appear in the document
4. If a field has multiple possible values, choose the most relevant one

"""

    if feedback:
        base_prompt += f"""
## Human Feedback (incorporate this in your extraction):
{feedback}

Please re-extract the data considering the feedback above. Make corrections as indicated.
"""

    base_prompt += """
## Output Format:
Respond with a valid JSON object containing:
{{
  "extracted_data": {{
    // field_name: extracted_value pairs matching the schema
  }},
  "confidence_scores": {{
    // field_name: confidence_score (0.0-1.0) pairs
  }},
  "extraction_notes": "Brief notes about the extraction, any uncertainties or issues"
}}
"""
    
    return base_prompt


def extract_data(state: ExtractionState) -> ExtractionState:
    """Extract data from the document using LLM."""
    
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0.1
    )
    
    prompt = create_extraction_prompt(
        state["document_text"],
        state["json_schema"],
        state.get("human_feedback")
    )
    
    messages = [
        SystemMessage(content="You are a precise document extraction agent. Always respond with valid JSON."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    
    try:
        # Parse the JSON response
        response_text = response.content
        
        # Handle markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        result = json.loads(response_text.strip())
        
        return {
            **state,
            "extracted_data": result.get("extracted_data", {}),
            "confidence_scores": result.get("confidence_scores", {}),
            "iteration": state["iteration"] + 1,
            "status": "extracted",
            "messages": [AIMessage(content=f"Extraction completed. Notes: {result.get('extraction_notes', 'None')}")]
        }
    except json.JSONDecodeError as e:
        return {
            **state,
            "extracted_data": {},
            "confidence_scores": {},
            "iteration": state["iteration"] + 1,
            "status": "error",
            "messages": [AIMessage(content=f"Error parsing extraction result: {str(e)}")]
        }


def validate_extraction(state: ExtractionState) -> ExtractionState:
    """Validate the extracted data against the schema."""
    
    schema = state["json_schema"]
    extracted = state.get("extracted_data", {})
    confidence = state.get("confidence_scores", {})
    
    # Check for required fields
    required_fields = schema.get("required", [])
    properties = schema.get("properties", {})
    
    missing_fields = []
    low_confidence_fields = []
    
    for field in required_fields:
        if field not in extracted or extracted[field] is None:
            missing_fields.append(field)
        elif field in confidence and confidence[field] < 0.7:
            low_confidence_fields.append(field)
    
    if missing_fields or low_confidence_fields:
        notes = []
        if missing_fields:
            notes.append(f"Missing required fields: {', '.join(missing_fields)}")
        if low_confidence_fields:
            notes.append(f"Low confidence fields: {', '.join(low_confidence_fields)}")
        
        return {
            **state,
            "status": "needs_review",
            "messages": [AIMessage(content=f"Validation: {'; '.join(notes)}")]
        }
    
    return {
        **state,
        "status": "validated",
        "messages": [AIMessage(content="All required fields extracted with good confidence.")]
    }


def check_feedback_needed(state: ExtractionState) -> Literal["wait_feedback", "end"]:
    """Determine if human feedback is needed."""
    
    if state["status"] == "needs_review":
        return "wait_feedback"
    
    if state["iteration"] >= state["max_iterations"]:
        return "end"
    
    return "end"


def apply_feedback(state: ExtractionState) -> ExtractionState:
    """Process and prepare for re-extraction with feedback."""
    
    return {
        **state,
        "status": "reprocessing",
        "messages": [HumanMessage(content=f"Applying feedback: {state.get('human_feedback', 'None')}")]
    }


def create_extraction_graph():
    """Create the LangGraph workflow for document extraction."""
    
    workflow = StateGraph(ExtractionState)
    
    # Add nodes
    workflow.add_node("extract", extract_data)
    workflow.add_node("validate", validate_extraction)
    workflow.add_node("apply_feedback", apply_feedback)
    
    # Set entry point
    workflow.set_entry_point("extract")
    
    # Add edges
    workflow.add_edge("extract", "validate")
    workflow.add_conditional_edges(
        "validate",
        check_feedback_needed,
        {
            "wait_feedback": END,  # Pause for human feedback
            "end": END
        }
    )
    workflow.add_edge("apply_feedback", "extract")
    
    # Compile with memory for checkpointing
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


class DocumentExtractionAgent:
    """Main agent class for document extraction with human-in-the-loop."""
    
    def __init__(self):
        self.graph = create_extraction_graph()
        self.sessions = {}
    
    def extract(
        self,
        document_text: str,
        json_schema: dict,
        session_id: str,
        feedback: Optional[str] = None
    ) -> dict:
        """
        Run extraction on a document.
        
        Args:
            document_text: The text content of the document
            json_schema: JSON schema defining fields to extract
            session_id: Unique session identifier for checkpointing
            feedback: Optional human feedback for re-extraction
        
        Returns:
            Extraction result with status and data
        """
        
        config = {"configurable": {"thread_id": session_id}}
        
        # Check if this is a re-run with feedback
        if feedback and session_id in self.sessions:
            prev_state = self.sessions[session_id]
            initial_state = {
                **prev_state,
                "human_feedback": feedback,
                "status": "reprocessing"
            }
        else:
            initial_state = {
                "document_text": document_text,
                "json_schema": json_schema,
                "extracted_data": None,
                "confidence_scores": None,
                "human_feedback": feedback,
                "iteration": 0,
                "max_iterations": 3,
                "status": "started",
                "messages": []
            }
        
        # Run the graph
        result = self.graph.invoke(initial_state, config)
        
        # Store session state
        self.sessions[session_id] = result
        
        return {
            "session_id": session_id,
            "status": result["status"],
            "extracted_data": result.get("extracted_data"),
            "confidence_scores": result.get("confidence_scores"),
            "iteration": result["iteration"],
            "needs_feedback": result["status"] == "needs_review"
        }
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get the current state of a session."""
        return self.sessions.get(session_id)


# Singleton instance
extraction_agent = DocumentExtractionAgent()


