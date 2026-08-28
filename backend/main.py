from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json, os, time
from google import genai
from google.genai import types
from backend.tools import update_model_config, restart_cloud_run_service, grant_temporary_iam_role

app = FastAPI(title="CreationsofH DevOps Agent API")

class IncidentPayload(BaseModel):
    telemetry_text: str

devops_tools = [update_model_config, restart_cloud_run_service, grant_temporary_iam_role]
tool_map = {
    "update_model_config": update_model_config,
    "restart_cloud_run_service": restart_cloud_run_service,
    "grant_temporary_iam_role": grant_temporary_iam_role
}

@app.post("/api/v1/remediate")
async def remediate_incident(payload: IncidentPayload):
    try:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise HTTPException(status_code=400, detail="GEMINI_API_KEY environment variable is not set.")

        client = genai.Client(api_key=api_key)

        system_prompt = (
            "You are DevOpsAgent by CreationsofH. You analyze infrastructure telemetry and stack traces. "
            "If an issue requires action, invoke the exact tool function: "
            "1. Use 'restart_cloud_run_service' for failing microservices. "
            "2. Use 'grant_temporary_iam_role' for permission/access errors. "
            "3. Use 'update_model_config' ONLY for codebase model configuration patches. "
            "If the prompt is an advisory question (like Docker best practices), answer conversationally without calling tools."
        )

        candidate_models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-3.5-flash"]
        response = None
        used_model = None
        last_error = None

        for model_target in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_target,
                    contents=[payload.telemetry_text],
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        tools=devops_tools,
                        temperature=0.1
                    )
                )
                if response:
                    used_model = model_target
                    break
            except Exception as err:
                last_error = err
                # If rate limited, sleep briefly before trying fallback candidate
                if "429" in str(err) or "RESOURCE_EXHAUSTED" in str(err):
                    time.sleep(2)
                continue

        if not response:
            if "429" in str(last_error) or "RESOURCE_EXHAUSTED" in str(last_error):
                return {
                    "status": "rate_limited",
                    "model_used": "none",
                    "tool_calls": [],
                    "diagnosis": "⚠️ **API Quota Exceeded (429 Rate Limit)**: The free tier limit for Gemini API was reached. Please wait ~60 seconds before retrying or upgrade to a paid billing project."
                }
            raise Exception(f"API Execution failed on candidate models. Last error: {str(last_error)}")

        tool_execution_results = []
        if response.function_calls:
            for call in response.function_calls:
                func_name = call.name
                func_args = dict(call.args)
                
                if func_name in tool_map:
                    execution_output = tool_map[func_name](**func_args)
                    tool_execution_results.append({
                        "name": func_name,
                        "args": func_args,
                        "result": json.loads(execution_output)
                    })

        return {
            "status": "success",
            "model_used": used_model,
            "tool_calls": tool_execution_results,
            "diagnosis": response.text if response.text else "Autonomous repair loop executed successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
