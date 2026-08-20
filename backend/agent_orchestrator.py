from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END, START

# 1. Define the State
class TutorState(TypedDict):
    student_id: str
    topic_id: str
    chat_history: list[dict]
    code_submission: str
    error_trace: str
    
    # Internal states passed between the 3 Multi-Agent nodes
    diagnosis_flag: str
    instructional_action: str
    final_output: str
    
    # The toggle for the empirical evaluation (Section 6.4)
    use_multi_agent_baseline: bool

# 2. Define the Single-Agent Monolith (Control Group)
def monolith_agent_node(state: TutorState) -> TutorState:
    """
    Control Group: Does diagnosis, pedagogical decision, and content selection
    in a single LLM prompt hop.
    """
    system_prompt = """
    You are an AI Python Tutor strictly operating as a Single-Agent Monolith.
    You must diagnose the code, plan the pedagogy, and generate the response.
    
    SLOW LEARNER RULES (MANDATORY):
    1. Concrete before abstract: Always use real-world analogies (e.g., 'boxes', 'recipes') before CS terms.
    2. Repetition without penalty: Never express frustration. If the student fails, try a visual metaphor.
    3. Mastery-gated: Do not advance to loops if variables are not mastered.
    """
    
    # Mocking LLM Execution with integrated Prompt
    return {
        **state,
        "final_output": f"Monolith (using slow-learner logic): {system_prompt} -> Evaluated {state.get('code_submission')}"
    }


# 3. Define the 3 Multi-Agent Nodes (Experimental Group)
def diagnostic_agent_node(state: TutorState) -> TutorState:
    """
    Node 1: Reasons purely over Python code and error traces to identify KTM misconceptions.
    Writes diagnosis asynchronously to LearnerModelService.
    """
    # LLM infers from state['code_submission'] and state['error_trace']
    inferred_gap = "Missing understanding of list mutability"
    
    return {
        **state,
        "diagnosis_flag": inferred_gap
    }

def pedagogical_agent_node(state: TutorState) -> TutorState:
    """
    Node 2: Decides *how* to teach based on the diagnosis and slow-learner strategy.
    Does not evaluate code, just plans the scaffolding.
    """
    pedagogical_rules = """
    You are the Pedagogical Agent. Given the diagnosis, output an instruction plan.
    SLOW LEARNER STRATEGIES:
    - If the gap is compounding (e.g. loops inside functions), decompose it.
    - Dictate 'Concrete-before-abstract' analogies.
    - Enforce 'Repetition tolerance'—offer 3 variations of the same concept.
    """
    
    # LLM infers from state['diagnosis_flag'] and LearnerModel style profile
    action = "Plan: Apply Concrete Analogy rule. Explain list mutability like a mutable physical box."
    
    return {
        **state,
        "instructional_action": action
    }

def content_agent_node(state: TutorState) -> TutorState:
    """
    Node 3: Generates the actual Python practice item or response based on the pedagogical plan.
    """
    # Uses state['instructional_action'] to craft exact output from MVP curriculum
    final_response = "Multi-Agent generated exercise: Let's compare a list to a mutable box..."
    
    return {
        **state,
        "final_output": final_response
    }


# 4. Define the Router (Avoids Orchestrator Agent LLM hop constraint)
def architecture_router(state: TutorState) -> Literal["monolith_agent", "diagnostic_agent"]:
    """
    Conditional edge: Reads the config flag to cleanly A/B test Section 6.4
    without spending an LLM inference token on routing.
    """
    if not state.get("use_multi_agent_baseline", True):
        return "monolith_agent"
    return "diagnostic_agent"


# 5. Build the Graph
builder = StateGraph(TutorState)

# Add Nodes
builder.add_node("monolith_agent", monolith_agent_node)
builder.add_node("diagnostic_agent", diagnostic_agent_node)
builder.add_node("pedagogical_agent", pedagogical_agent_node)
builder.add_node("content_agent", content_agent_node)

# Add Edges (Control Group)
builder.add_edge("monolith_agent", END)

# Add Edges (Multi-Agent Experimental Pipeline)
builder.add_edge("diagnostic_agent", "pedagogical_agent")
builder.add_edge("pedagogical_agent", "content_agent")
builder.add_edge("content_agent", END)

# Conditional Entry Point Router (Section 6.4 Toggle)
builder.add_conditional_edges(
    START,
    architecture_router,
    {
        "monolith_agent": "monolith_agent",
        "diagnostic_agent": "diagnostic_agent"
    }
)

tutor_graph = builder.compile()

# Example usage to prove it works:
# result = tutor_graph.invoke({"use_multi_agent_baseline": True, "student_id": "123", "code_submission": "list = []"})
