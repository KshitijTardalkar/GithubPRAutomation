from crewai import  Crew
from services.ai_services.crew.agent import code_review_agent
from services.ai_services.crew.task import code_analysis_task

crew = Crew(
    #Specify the agents available in the crew
    agents=[code_review_agent],

    #Specify the tasks the crew completes
    tasks=[code_analysis_task],
)