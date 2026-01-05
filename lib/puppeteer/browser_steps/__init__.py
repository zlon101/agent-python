"""
浏览器步骤自动化模块
"""

from .step_executor import (
    BrowserStepExecutor,
    StepConfig,
    StepType,
    create_navigate_step,
    create_click_step,
    create_input_step,
    create_select_step,
    create_extract_step,
    create_press_key_step,
    create_wait_step
)

__all__ = [
    'BrowserStepExecutor',
    'StepConfig',
    'StepType',
    'create_navigate_step',
    'create_click_step',
    'create_input_step',
    'create_select_step',
    'create_extract_step',
    'create_press_key_step',
    'create_wait_step',
]
