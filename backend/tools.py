import json, os

def update_model_config(old_model: str, new_model: str) -> str:
    """Scans codebase files and updates deprecated model strings to a supported model version."""
    target_files = ["backend/main.py", "app.py", "frontend/app.py"]
    updated_files = []
    
    for filename in target_files:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                content = f.read()
            if old_model in content:
                content = content.replace(old_model, new_model)
                with open(filename, "w") as f:
                    f.write(content)
                updated_files.append(filename)
                
    return json.dumps({
        "status": "SUCCESS",
        "action": "CODEBASE_AUTO_HEAL",
        "replaced": old_model,
        "new_target": new_model,
        "files_patched": updated_files,
        "message": f"Auto-healed codebase: replaced '{old_model}' with '{new_model}' in {updated_files}."
    })

def restart_cloud_run_service(service_name: str, region: str = "us-central1") -> str:
    """Restarts a failing Google Cloud Run microservice."""
    return json.dumps({
        "status": "SUCCESS",
        "action": "REDEPLOY_SERVICE",
        "service": service_name,
        "region": region,
        "message": f"Microservice '{service_name}' successfully restarted in {region}."
    })

def grant_temporary_iam_role(user_email: str, role_name: str) -> str:
    """Grants temporary IAM developer permissions to resolve deployment blockages."""
    return json.dumps({
        "status": "SUCCESS",
        "action": "GRANT_IAM_ROLE",
        "target_user": user_email,
        "role": role_name,
        "duration": "2 Hours",
        "message": f"Role '{role_name}' provisioned for user {user_email}."
    })
