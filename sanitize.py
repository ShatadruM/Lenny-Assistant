import os
import re

source_file = r"C:\Users\shata\.gemini\antigravity-ide\brain\b2cfa3a0-58bd-44f2-bd24-609789fee68f\.system_generated\logs\transcript.jsonl"
dest_dir = r"c:\Users\shata\Desktop\projects\oogway\agent_transcripts"
dest_file = os.path.join(dest_dir, "transcript.jsonl")

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# Regex patterns for common keys and connection strings
patterns = [
    (re.compile(r'sk-[A-Za-z0-9-_]{32,}'), '[REDACTED_OPENAI_KEY]'),
    (re.compile(r'sk-ant-[A-Za-z0-9-_]+'), '[REDACTED_ANTHROPIC_KEY]'),
    (re.compile(r'gsk_[A-Za-z0-9-_]+'), '[REDACTED_GROQ_KEY]'),
    (re.compile(r'postgresql://[^:]+:[^@]+@'), 'postgresql://[REDACTED_USER]:[REDACTED_PASSWORD]@')
]

if os.path.exists(source_file):
    with open(source_file, 'r', encoding='utf-8') as fin, open(dest_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            sanitized_line = line
            for pattern, replacement in patterns:
                sanitized_line = pattern.sub(replacement, sanitized_line)
            fout.write(sanitized_line)
    print("Transcript sanitized and saved.")
else:
    print("Source transcript not found.")
