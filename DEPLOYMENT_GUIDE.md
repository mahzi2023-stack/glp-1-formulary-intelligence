# 🚀 DEPLOYMENT GUIDE

This folder contains everything you need to deploy the GLP-1 Formulary Intelligence app to Streamlit Cloud.

## 📦 WHAT'S IN THIS FOLDER

```
github_upload/
├── app_streamlit.py          ⭐ Main Streamlit app
├── extract_glp1_coverage.py  ⭐ Extraction engine
├── glp1_ndcs.txt            ⭐ NDC reference list
├── requirements.txt         ⭐ Python dependencies
├── README.md                📄 Documentation
├── .gitignore              🚫 Git ignore rules
├── sample_data/            📁 Demo data (6 plans)
│   ├── plan_information.txt
│   ├── basic_drugs_formulary.txt
│   └── beneficiary_cost.txt
└── DEPLOYMENT_GUIDE.md     📖 This file
```

## 🎯 QUICK DEPLOYMENT (5 MINUTES)

### Step 1: Create GitHub Repository

1. Go to **https://github.com/new**
2. Repository name: `glp1-formulary-intelligence`
3. Description: `Medicare Part D GLP-1 formulary coverage analysis`
4. Visibility: **Public** (required for free Streamlit hosting)
5. Click **"Create repository"**

### Step 2: Upload Files

**Option A: Web Interface** (easiest)

1. Click **"uploading an existing file"** link on the new repo page
2. Drag ALL files from this `github_upload/` folder into the browser
3. GitHub will automatically preserve folder structure
4. Commit message: `Initial deployment`
5. Click **"Commit changes"**

**Option B: Command Line**

```bash
cd /path/to/github_upload

git init
git add .
git commit -m "Initial deployment"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/glp1-formulary-intelligence.git
git push -u origin main
```

### Step 3: Deploy to Streamlit Cloud

1. Go to **https://share.streamlit.io** (or **https://streamlit.io/cloud**)
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository**: `YOUR-USERNAME/glp1-formulary-intelligence`
   - **Branch**: `main`
   - **Main file path**: `app_streamlit.py`
5. Click **"Deploy!"**

**DONE!** Your app will be live in 2-3 minutes at:
```
https://glp1-formulary-intelligence-[random].streamlit.app
```

## 📊 WHAT THE APP DOES

Once deployed, users can:

✅ **Load demo data** - 6 sample Medicare Part D plans  
✅ **Upload CMS files** - Analyze their own data  
✅ **View dashboards** - Interactive charts and metrics  
✅ **Filter plans** - By organization, product, access score  
✅ **Export results** - CSV and JSON downloads  

## 🔄 UPDATE YOUR APP

After deployment, to update the app:

1. Make changes to files in this folder
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push
   ```
3. Streamlit Cloud auto-deploys within 1 minute

## 📈 LOAD REAL DATA

Once deployed, users can upload the full CMS dataset:

1. Download from: https://data.cms.gov/provider-summary-by-type-of-service/medicare-part-d-prescribers/monthly-prescription-drug-plan-formulary-and-pharmacy-network-information
2. Extract the ZIP file
3. In the app, click "Upload CMS Files"
4. Upload these 3 files:
   - `PlanInformation_YYYY.txt` → rename to `plan_information.txt`
   - `BasicDrugsFormulary_YYYY.txt` → rename to `basic_drugs_formulary.txt`
   - `BeneficiaryCost_YYYY.txt` → rename to `beneficiary_cost.txt`

## 🔧 TROUBLESHOOTING

**App won't deploy?**
- Check `requirements.txt` is included
- Ensure `app_streamlit.py` is in root directory
- Repository must be public for free hosting

**Demo data not loading?**
- Check `sample_data/` folder exists
- Verify folder structure matches expected format

**Upload fails?**
- CMS files must be pipe-delimited text (`.txt`)
- Files must have correct column headers
- Check file size (should be <500MB each)

## 💡 CUSTOMIZATION

Want to customize the app?

**Change branding:**
- Edit line 19-20 in `app_streamlit.py` (page title)
- Edit line 32-33 (header text)

**Modify demo data:**
- Replace files in `sample_data/` folder
- Must maintain same structure

**Add more products:**
- Edit `glp1_ndcs.txt` (add NDC codes)
- Update product list in extraction logic

## 📞 SUPPORT

Issues? Check:
- Streamlit docs: https://docs.streamlit.io
- CMS data docs: https://data.cms.gov
- GitHub issues in your repo

## 🎉 SUCCESS METRICS

After deployment, you'll have:

✅ **Free hosting** - $0/month (Streamlit Cloud free tier)  
✅ **Public URL** - Share with anyone  
✅ **Auto-updates** - Push to GitHub, app updates automatically  
✅ **Analytics** - See usage metrics in Streamlit dashboard  
✅ **99.9% uptime** - Streamlit's infrastructure  

---

**Total deployment time: 5 minutes**  
**Cost: $0**  
**Maintenance: Push updates to GitHub as needed**
