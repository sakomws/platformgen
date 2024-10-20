**PlatformGen**

**How to use**
1. To Access dependencies of a repo: run `python access_dep.py`. Writes dependencies to project_dep
2. To search for new versions: run `python new_dep_search.py`. Writes up to date dependencies to `up_to_date_dependencies.txt` and dependencies to update to `updates_available.txt`
3. To search for all new versions of dependencies and info on new releases run `python new_version_tldr.py` which writes the info on new versions to `version_updates_tldr.txt`
4. To summarize all info on new versions run `python version_summary.py` which writes succinct summaries of the new versions to `new_version_updates_summary.txt`
5. Run `python -m http.server 8000` to access PlatformGen Dashboard and:
   - View all the dependency summaries
   - Approve/reject dependency changes
   - Create a PR with approved dependency changes
  
**Next**
- Take action (create the PR) when the user approves and creates the PR _(via the UI)_
- Improve UI (V0)
- Make pipeline more robust (support/test many repos)
- Integrate Lambda/Nebius for inference - https://docs.nebius.ai/studio/inference/
