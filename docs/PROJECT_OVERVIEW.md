# Project Overview

## Problem
Turning a software idea into a working project requires planning, coding, testing and debugging. A simple chatbot that only returns code does not complete this workflow.

## Proposed solution
PS02 coordinates specialized agents to plan a project, generate source files, run basic checks, optionally execute Python in Docker and provide a code review.

## Objectives
- Convert natural-language requirements into a task plan.
- Generate related project files.
- Run syntax checks and unit tests.
- Optionally execute Python in a constrained Docker container.
- Produce review notes and a downloadable ZIP.

## Agent responsibilities
- Planner: requirements and task breakdown.
- Developer: source-file generation.
- Tester: syntax and unit-test checks.
- Debugger: bounded repair proposal when checks fail.
- Reviewer: quality and risk feedback.
- Orchestrator: controls workflow and saves results.

## Evaluation metrics
Task completion rate, syntax pass rate, unit-test pass rate, repair success rate, median completion time, model cost and human review score.

## Risks
Hallucinated code, unsafe generated programs, API cost, ambiguous requirements and unbounded agent loops. Mitigations include independent tests, restricted Docker execution, human review, token controls and bounded repair iterations.
