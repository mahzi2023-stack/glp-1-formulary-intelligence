# 💊 GLP-1 Formulary Intelligence Platform

**Automated Medicare Part D coverage analysis for GLP-1 drugs**

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)](https://streamlit.io)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Quick Start

**Run Locally:**
```bash
pip install -r requirements.txt
streamlit run app_streamlit.py
```

**Live Demo:** Deploy to Streamlit Cloud for instant public URL (see DEPLOYMENT_GUIDE.md)

---

## 📊 What This Does

Extracts and analyzes Medicare Part D formulary coverage for GLP-1 drugs:

- **Wegovy** (semaglutide, obesity)
- **Ozempic** (semaglutide, diabetes)  
- **Zepbound** (tirzepatide, obesity)
- **Mounjaro** (tirzepatide, diabetes)

### Features

✅ **Upload CMS data** - Analyze 800+ Medicare Part D plans  
✅ **Access scoring** - Composite 0-100 score based on tier, PA, ST, QL, cost  
✅ **Interactive dashboards** - Charts, filters, plan lookup  
✅ **Export results** - CSV and JSON downloads  
✅ **Zero cost** - Free public data, free hosting  

---

## 🎯 Use Cases

**For Pharmaceutical Companies:**
- Track formulary access trends
- Identify contracting opportunities
- Benchmark against competitors

**For Payers:**
- Analyze peer formulary designs
- Benchmark PA/ST rates
- Support utilization management

**For Researchers:**
- Study coverage patterns
- Access disparities (obesity vs diabetes)
- Market dynamics

---

## 📂 Data Sources

**CMS Public Use Files** (free):
- Monthly Prescription Drug Plan Formulary Files
- Download: https://data.cms.gov/provider-summary-by-type-of-service/medicare-part-d-prescribers
- Updated monthly (~26th of each month)

---

## 📈 Key Findings (Demo Data)

From production run of 848 plans:

| Product | Avg Access Score | PA Rate | ST Rate |
|---------|-----------------|---------|---------|
| **Ozempic** (diabetes) | 74.1 | 19% | 15% |
| **Mounjaro** (diabetes) | 66.3 | 33% | 26% |
| **Wegovy** (obesity) | 41.6 | 87% | 41% |
| **Zepbound** (obesity) | 28.5 | 95% | 77% |

**Key Insight:** 2x access disparity between diabetes and obesity indications despite same molecules.

---

## 🛠️ Tech Stack

- **Python 3.8+** - Core logic
- **Streamlit** - Web interface
- **Pandas** - Data processing
- **Plotly** - Interactive charts

**No database required** - runs entirely on CSV files!

---

## 💻 Usage

### Option 1: Use Demo Data (6 plans)

```bash
streamlit run app_streamlit.py
```

Click **"Load Demo Data"** in sidebar.

### Option 2: Upload Full CMS Data (800+ plans)

1. Download from CMS website (link above)
2. Extract ZIP file
3. In app sidebar, click **"Upload CMS Files"**
4. Upload these 3 files:
   - `PlanInformation_YYYY.txt`
   - `BasicDrugsFormulary_YYYY.txt`
   - `BeneficiaryCost_YYYY.txt`

---

## 🌐 Deploy to Cloud (Free)

See **DEPLOYMENT_GUIDE.md** for detailed instructions.

**Quick deploy:**
1. Push this repo to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo and deploy!

---

## 📊 Project Structure

```
glp1-formulary-intelligence/
├── app_streamlit.py              # Main Streamlit app
├── extract_glp1_coverage.py      # Extraction engine
├── glp1_ndcs.txt                # NDC reference list
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── DEPLOYMENT_GUIDE.md          # Deployment instructions
├── .gitignore                  # Git ignore rules
└── sample_data/                # Demo data (6 plans)
    ├── plan_information.txt
    ├── basic_drugs_formulary.txt
    └── beneficiary_cost.txt
```

---

## 💰 Cost Comparison

| Solution | Annual Cost |
|----------|-------------|
| **MMIT Subscription** | $50,000 - $200,000 |
| **This App** | **$0** |

**ROI: Infinite** 🚀

---

## 📝 License

MIT License

---

## ⭐ Star This Repo

If you find this useful, please star the repo!

---

**Built with ❤️ for improving patient access to GLP-1 medications**
