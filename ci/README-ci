# CI / AgentOps Pipeline

This folder contains the Continuous Evaluation (CE) pipeline used to enforce
quality and prevent regressions in Aegis.

## Files

### `premerge-eval.yml`
A GitHub Actions workflow that runs on every pull request:
- Installs dependencies  
- Runs unit tests  
- Executes the Golden Dataset evaluation  
- Fails the PR if the mean LLM-judge score is below the threshold  
- Implements AgentOps "evaluation-gated deployment"  

### `run_golden_eval.py`
A safe, mocked evaluation script which:
- Loads the golden dataset  
- Runs each mission through the agent pipeline  
- Applies judge scoring  
- Computes mean score  
- Exits with non-zero status if threshold not met  

This enforces:
- Safety  
- Reliability  
- Stability  
- Continuous improvement  

## Relevance to Capstone
This CI pipeline demonstrates:
- **Evaluation-gated deployment**  
- **AgentOps best practices**  
- **Continuous integration with metrics enforcement**  
- **Consistent regression prevention**  

This matches Day 4 and Day 5 of the AI Agents Intensive course.
