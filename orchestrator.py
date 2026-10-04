import logging
from human_engine import run_human_engine
from anti_engine import run_anti_engine
from ast_verifier import verify_code

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_engine_with_retries(engine_name, engine_func, task_prompt, max_retries=3):
    last_error = ""
    
    for attempt in range(1, max_retries + 1):
        # On retry, feed the exact error back to the AI so it can correct it
        if attempt == 1:
            current_prompt = task_prompt
        else:
            current_prompt = f"{task_prompt}\n\nCRITICAL FIX REQUIRED: Previous attempt failed with this error:\n{last_error}\nEnsure the function is named strictly as requested and contains no test runner code."
            
        code = engine_func(current_prompt)
        
        is_valid, error_msg = verify_code(code)
        
        if is_valid:
            return True, code, attempt
        else:
            last_error = error_msg
            logger.error(f"[{engine_name} - Attempt {attempt}/{max_retries}]\nFailed: {error_msg}\n")
            
    logger.error(f"❌ {engine_name} exhausted all retries and failed.\n")
    return False, None, max_retries

def orchestrate(task_prompt):
    # 1. Try Human Engine first
    human_success, human_code, human_attempts = run_engine_with_retries(
        "HUMAN ENGINE", run_human_engine, task_prompt
    )
    
    if human_success:
        return {
            "status": "SUCCESS",
            "winning_engine": "HUMAN ENGINE",
            "human_score": 100.0,
            "anti_score": 0.0,
            "verified_code": human_code
        }
        
    # 2. If Human Engine fails, try Anti Engine
    anti_success, anti_code, anti_attempts = run_engine_with_retries(
        "ANTI ENGINE", run_anti_engine, task_prompt
    )
    
    if anti_success:
        return {
            "status": "SUCCESS",
            "winning_engine": "ANTI ENGINE",
            "human_score": 0.0,
            "anti_score": 100.0,
            "verified_code": anti_code
        }
        
    # 3. If both engines fail all retries
    return {
        "status": "FAILED",
        "winning_engine": None,
        "human_score": 0.0,
        "anti_score": 0.0,
        "verified_code": None
    }