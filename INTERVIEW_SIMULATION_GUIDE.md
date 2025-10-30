# 🎯 Interview Simulation Setup Guide

## Overview
This guide helps you set up and use a comprehensive interview simulation system using your MCP-powered digital twin with real job postings from Seek.com.au.

## 📁 Files Created

### Core Interview System:
- `job-postings/` - Directory for job posting files
- `job-postings/job-template.md` - Template for new job postings
- `job-postings/job1.md` - Sample job posting (replace with real one)
- `interview_simulation_prompts.md` - Ready-to-use Copilot prompts
- `digitaltwin_enhanced.json` - Enhanced profile with STAR format
- `update_profile.py` - Script to update your profile

### Supporting Files:
- `digital_twin_mcp_server.py` - MCP server (already working)
- `test_mcp_server.py` - Test script
- `.vscode/settings.json` - VS Code MCP configuration

## 🚀 Quick Start (5 minutes)

### Step 1: Get a Real Job Posting
1. Go to https://www.seek.com.au/
2. Search for jobs matching your skills (e.g., "junior developer", "full stack developer")
3. Find a realistic job that interests you
4. Copy the ENTIRE job posting content

### Step 2: Create Your Job File
```bash
# Copy the template
cp job-postings/job-template.md job-postings/my-real-job.md

# Open in VS Code
code job-postings/my-real-job.md
```

Replace the template content with your real job posting from Seek.

### Step 3: Enhance Your Profile (Optional but Recommended)
```bash
# Update your profile with enhanced data
python update_profile.py
```

### Step 4: Start Interview Simulation
1. Open GitHub Copilot Chat in VS Code Insiders
2. Copy a prompt from `interview_simulation_prompts.md`
3. Replace `job-postings/job1.md` with `job-postings/my-real-job.md` in the prompt
4. Paste and run the interview simulation

## 📋 Interview Simulation Process

### 🔥 Recommended Order:

1. **Critical Recruiter Screening** (Do this first!)
   - Most important assessment
   - Identifies major gaps quickly
   - Pass/fail decision point

2. **Technical Interview**
   - Deep technical assessment
   - Specific to job requirements
   - Skill competency ratings

3. **Hiring Manager Interview**
   - Role fit evaluation
   - Team collaboration assessment
   - Growth potential review

4. **Additional Personas** (Optional)
   - HR screening
   - Project manager assessment
   - Executive interview

### 🎯 Success Criteria:

| Interview Type | Target Score | Must-Have |
|---------------|-------------|-----------|
| Critical Recruiter | 7+ overall | HIRE recommendation |
| Technical | 7+ core skills | Pass on required tech |
| Hiring Manager | 8+ role fit | Strong team fit |

## 🛠️ Troubleshooting

### MCP Server Issues:
```bash
# Test MCP server
python test_mcp_server.py

# Start MCP server manually
python digital_twin_mcp_server.py
```

### GitHub Copilot Not Using MCP:
1. Ensure VS Code Insiders (not regular VS Code)
2. Check `.vscode/settings.json` exists
3. Restart VS Code Insiders
4. Use `@workspace` prefix in prompts
5. Try in a new Copilot Chat session

### Profile Update Issues:
```bash
# Check current profile
cat digitaltwin.json | head -20

# Update with enhanced version
python update_profile.py

# Test updated profile
python test_mcp_server.py
```

## 📊 Using the Results

### After Each Interview:
1. **Save the feedback** - Copy Copilot's assessment to a document
2. **Identify patterns** - Look for consistent weaknesses across interviews
3. **Update profile** - Add missing information to `digitaltwin_enhanced.json`
4. **Re-embed** - Run `python update_profile.py` after changes
5. **Re-test** - Try the same interview again with updated profile

### Common Improvement Areas:
- **Salary expectations** - Add realistic salary ranges
- **Location preferences** - Specify work location flexibility
- **Technical depth** - Add specific technology experience levels
- **Project examples** - Use STAR format for better storytelling
- **Soft skills** - Add concrete examples of teamwork, leadership
- **Commercial experience** - Highlight any real-world application impact

## 🎯 Advanced Usage

### Multiple Job Testing:
```bash
# Create additional job files
cp job-postings/job-template.md job-postings/job2.md
cp job-postings/job-template.md job-postings/job3.md

# Test different job types:
# - Junior developer positions
# - Mid-level roles (stretch goals)
# - Different tech stacks
# - Various company sizes
```

### Profile Iteration:
1. **Baseline Test** - Run initial interview with current profile
2. **Enhance Profile** - Add missing information identified in feedback
3. **Re-test** - Run same interview with enhanced profile
4. **Compare Results** - Document improvements in scores
5. **Repeat** - Continue iterating until achieving target scores

### Different Interview Styles:
- **Startup Interview** - Fast-paced, practical focus
- **Corporate Interview** - Process-oriented, cultural fit
- **Technical Company** - Deep technical assessment
- **Consulting Interview** - Problem-solving, client interaction

## 🎉 Success Metrics

### Ready for Real Interviews When:
- ✅ Critical Recruiter gives HIRE recommendation (8+/10)
- ✅ Technical Interview scores 7+ on required skills
- ✅ Hiring Manager rates role fit as 8+/10
- ✅ Consistent positive feedback across multiple job types
- ✅ No major knowledge gaps identified
- ✅ Salary/location expectations align with market

### Continuous Improvement:
- Run simulations weekly with new job postings
- Track improvement over time
- Practice with increasingly challenging roles
- Refine your profile based on market feedback

---

**🚀 Ready to start? Run your first Critical Recruiter Screening now!**

1. Find a job on Seek.com.au
2. Update `job-postings/job1.md` with real content
3. Copy the Critical Recruiter prompt from `interview_simulation_prompts.md`
4. Paste into GitHub Copilot Chat with `@workspace` prefix
5. Get your first professional assessment!

The goal is to receive a HIRE recommendation from the critical recruiter screening. Once you achieve that consistently, you'll be ready for real interviews! 🎯