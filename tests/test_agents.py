import pytest
from app.agent import root_agent
from app.sub_agents.profiler import profiler_agent
from app.sub_agents.curator import curator_agent
from app.sub_agents.synthesizer import synthesizer_agent
from app.sub_agents.critic import critic_agent
from app import app


def test_agent_structure_and_sub_agents():
    assert root_agent.name == "cloud_newsletter_orchestrator"
    assert len(root_agent.sub_agents) == 4
    
    sub_agent_names = [sa.name for sa in root_agent.sub_agents]
    assert "customer_profiler_agent" in sub_agent_names
    assert "release_notes_curator_agent" in sub_agent_names
    assert "newsletter_synthesizer_agent" in sub_agent_names
    assert "fact_checking_critic_agent" in sub_agent_names


def test_agent_tools_registration():
    assert len(root_agent.tools) == 5
    assert len(profiler_agent.tools) == 2
    assert len(curator_agent.tools) == 2
    assert len(synthesizer_agent.tools) == 1


def test_app_configuration():
    assert app.name == "app"
    assert app.root_agent == root_agent
