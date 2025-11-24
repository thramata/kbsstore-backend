#!/usr/bin/env bash
cd "/Users/mac/Documents/kbsstore-backend"
source venv/bin/activate
uvicorn main:app --reload
