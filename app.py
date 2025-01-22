#!/usr/bin/env python3
from aws_cdk import App
from stacks.stage1_stack import Stage1Stack

app = App()
Stage1Stack(app, "HabitSlapStage1Stack")
app.synth()
