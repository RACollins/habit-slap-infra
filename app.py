#!/usr/bin/env python3
from aws_cdk import App
from stacks.stage1_stack import Stage1Stack
from stacks.stage2_stack import Stage2Stack

app = App()
Stage1Stack(app, "HabitSlapStage1Stack")
Stage2Stack(app, "HabitSlapStage2Stack")
app.synth()
