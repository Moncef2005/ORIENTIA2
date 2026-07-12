from fastapi import APIRouter, HTTPException
from app.models.schemas import AgentChatRequest
from app.services.agent import run_agent

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat")
async def chat(request: AgentChatRequest):
    try:
        messages = [m.model_dump() for m in request.messages]
        full_trace = await run_agent(messages)
        # Only return what the frontend needs: the final assistant text +
        # a compact trace of which tools fired (nice for a "thinking" UI).
        final_message = next(
            (m for m in reversed(full_trace) if m["role"] == "assistant" and m.get("content")),
            None,
        )
        tool_trace = [
            {"tool": m["name"], "result": m["content"]}
            for m in full_trace
            if m["role"] == "tool"
        ]
        return {
            "reply": final_message["content"] if final_message else "",
            "tool_trace": tool_trace,
        }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
