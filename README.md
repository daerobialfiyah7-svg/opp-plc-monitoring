# OPP Process Performance Monitoring — Phase 1

This is a Streamlit Community Cloud-ready prototype built from the supplied PLC exports.

## Included real PLC history
- 24022026.xlsx
- 25022026.xlsx
- 26022026.xlsx
- 4,320 historical timestamps
- 461 PLC tags
- 1-minute interval

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository, for example `opp-plc-monitoring`.
2. Upload ALL files/folders in this project to the repository root.
3. Go to https://share.streamlit.io/
4. Sign in and choose **Create app**.
5. Select your repository, branch `main`, and file `streamlit_app.py`.
6. Choose an app URL such as `opp-plc-monitoring`.
7. Click **Deploy**.

The repository includes `requirements.txt`, which tells Community Cloud which Python packages to install.

## Important
This is Phase 1. The current upload control validates a new Excel file but does not yet persist new uploads to a production database. Phase 2 will add PostgreSQL persistence, duplicate protection, continuity checks, tag master, and permanent daily append.
