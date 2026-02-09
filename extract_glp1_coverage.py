#!/usr/bin/env python3
"""
Medicare Part D GLP-1 Coverage Extractor
Extracts formulary coverage details for GLP-1 RA drugs across all Part D plans

Data Source: CMS Monthly Prescription Drug Plan Formulary and Pharmacy Network Information
File Format: Pipe-delimited (|) text files

Output: Comprehensive coverage matrix with:
- Administrative Friction (PA, ST, QL)
- Addressable Market (tier placement, ST criteria indicators)
- Affordability (copay/coinsurance by tier and pharmacy type)
"""

import csv
import zipfile
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import json

@dataclass
class GLP1Product:
    """GLP-1 RA product definition"""
    name: str
    molecule: str  # semaglutide or tirzepatide
    indication: str  # obesity or diabetes
    manufacturer: str  # Novo Nordisk or Eli Lilly
    ndcs: List[str]  # List of NDC codes for all strengths

@dataclass
class FormularyRecord:
    """Individual formulary coverage record"""
    contract_id: str
    plan_id: str
    ndc: str
    tier: str
    prior_auth: bool  # PA indicator
    step_therapy: bool  # ST indicator
    quantity_limit: bool  # QL indicator
    
@dataclass
class BeneficiaryCostRecord:
    """Cost-sharing details"""
    contract_id: str
    plan_id: str
    tier: str
    cost_type: str  # copay or coinsurance
    retail_preferred_cost: float
    retail_standard_cost: float
    mail_order_cost: float

@dataclass
class PlanInfo:
    """Plan identification"""
    contract_id: str
    plan_id: str
    plan_name: str
    plan_type: str  # PDP or MA-PD
    organization_name: str

@dataclass
class CoverageAnalysis:
    """Complete coverage analysis for one product in one plan"""
    # Plan identifiers
    contract_id: str
    plan_id: str
    plan_name: str
    plan_type: str
    organization_name: str
    
    # Product
    product_name: str
    molecule: str
    indication: str
    
    # Administrative Friction
    covered: bool
    tier: str
    prior_auth: bool
    step_therapy: bool
    quantity_limit: bool
    
    # Affordability 
    cost_type: str  # copay or coinsurance
    retail_preferred_cost: float
    retail_standard_cost: float
    mail_order_cost: float
    
    # Composite Score (for ranking)
    access_score: float  # 0-100, higher = better access


class GLP1CoverageExtractor:
    """Extract and analyze GLP-1 coverage from Medicare Part D formulary files"""
    
    # GLP-1 Product Definitions
    PRODUCTS = [
        GLP1Product(
            name="Wegovy",
            molecule="semaglutide",
            indication="obesity",
            manufacturer="Novo Nordisk",
            ndcs=["00169451701", "00169453001", "00169457401", "00169459301", "00169476401"]
        ),
        GLP1Product(
            name="Ozempic",
            molecule="semaglutide",
            indication="diabetes",
            manufacturer="Novo Nordisk",
            ndcs=["00169406001", "00169396701", "00169482301"]
        ),
        GLP1Product(
            name="Zepbound",
            molecule="tirzepatide",
            indication="obesity",
            manufacturer="Eli Lilly",
            ndcs=["00002466601", "00002466701", "00002466801", "00002466901", "00002467001", "00002467101"]
        ),
        GLP1Product(
            name="Mounjaro",
            molecule="tirzepatide",
            indication="diabetes",
            manufacturer="Eli Lilly",
            ndcs=["00002230001", "00002240001", "00002250001", "00002260001", "00002270001", "00002280001"]
        ),
    ]
    
    def __init__(self, data_dir: Path):
        """
        Initialize extractor
        
        Args:
            data_dir: Directory containing extracted CMS formulary files
        """
        self.data_dir = Path(data_dir)
        self.products = {p.name: p for p in self.PRODUCTS}
        
        # Build NDC -> Product mapping
        self.ndc_to_product: Dict[str, str] = {}
        for product in self.PRODUCTS:
            for ndc in product.ndcs:
                # Normalize NDC (remove dashes, ensure 11 digits)
                normalized = ndc.replace("-", "")
                self.ndc_to_product[normalized] = product.name
    
    def normalize_ndc(self, ndc: str) -> str:
        """
        Normalize NDC to 11-digit format without dashes
        
        Handles both formats:
        - 5-4-2 format: 00169-4517-01 -> 00169451701
        - 11-digit: 00169451701 -> 00169451701
        """
        # Remove all dashes first
        ndc_clean = ndc.replace("-", "")
        
        # If already 11 digits, return as-is
        if len(ndc_clean) == 11:
            return ndc_clean
        
        # If shorter, pad to 11 digits (shouldn't happen with valid NDCs)
        return ndc_clean.zfill(11)
    
    def parse_formulary_file(self, filepath: Path) -> List[FormularyRecord]:
        """
        Parse Basic Drugs Formulary file
        
        Expected columns (pipe-delimited):
        - Contract_ID
        - Plan_ID  
        - NDC
        - Tier
        - Prior_Authorization (Y/N)
        - Step_Therapy (Y/N)
        - Quantity_Limit (Y/N)
        """
        records = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='|')
            
            for row in reader:
                # Normalize NDC and check if it's a GLP-1
                ndc = self.normalize_ndc(row.get('NDC', ''))
                
                if ndc in self.ndc_to_product:
                    record = FormularyRecord(
                        contract_id=row.get('Contract_ID', ''),
                        plan_id=row.get('Plan_ID', ''),
                        ndc=ndc,
                        tier=row.get('Tier', ''),
                        prior_auth=row.get('Prior_Authorization', 'N').upper() == 'Y',
                        step_therapy=row.get('Step_Therapy', 'N').upper() == 'Y',
                        quantity_limit=row.get('Quantity_Limit', 'N').upper() == 'Y'
                    )
                    records.append(record)
        
        return records
    
    def parse_cost_file(self, filepath: Path) -> List[BeneficiaryCostRecord]:
        """
        Parse Beneficiary Cost file
        
        Expected columns:
        - Contract_ID
        - Plan_ID
        - Tier
        - Cost_Type (copay or coinsurance)
        - Retail_Preferred_Cost
        - Retail_Standard_Cost  
        - Mail_Order_Cost
        """
        records = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='|')
            
            for row in reader:
                try:
                    record = BeneficiaryCostRecord(
                        contract_id=row.get('Contract_ID', ''),
                        plan_id=row.get('Plan_ID', ''),
                        tier=row.get('Tier', ''),
                        cost_type=row.get('Cost_Type', '').lower(),
                        retail_preferred_cost=float(row.get('Retail_Preferred_Cost', 0) or 0),
                        retail_standard_cost=float(row.get('Retail_Standard_Cost', 0) or 0),
                        mail_order_cost=float(row.get('Mail_Order_Cost', 0) or 0)
                    )
                    records.append(record)
                except (ValueError, TypeError):
                    # Skip malformed cost records
                    continue
        
        return records
    
    def parse_plan_info_file(self, filepath: Path) -> Dict[Tuple[str, str], PlanInfo]:
        """
        Parse Plan Information file
        
        Returns: Dict mapping (contract_id, plan_id) -> PlanInfo
        """
        plans = {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='|')
            
            for row in reader:
                key = (row.get('Contract_ID', ''), row.get('Plan_ID', ''))
                plans[key] = PlanInfo(
                    contract_id=row.get('Contract_ID', ''),
                    plan_id=row.get('Plan_ID', ''),
                    plan_name=row.get('Plan_Name', ''),
                    plan_type=row.get('Plan_Type', ''),
                    organization_name=row.get('Organization_Name', '')
                )
        
        return plans
    
    def calculate_access_score(self, coverage: CoverageAnalysis) -> float:
        """
        Calculate composite access score (0-100)
        
        Higher score = better access
        
        Scoring:
        - Not covered: 0
        - Tier: T1=40, T2=35, T3=30, T4=25, T5=20, T6=15, Specialty=10
        - No PA: +20, PA: +0
        - No ST: +20, ST: +0  
        - No QL: +10, QL: +0
        - Cost (copay): <$50=+10, $50-100=+5, >$100=+0
        - Cost (coinsurance): <25%=+10, 25-33%=+5, >33%=+0
        """
        if not coverage.covered:
            return 0.0
        
        score = 0.0
        
        # Tier scoring
        tier_scores = {
            '1': 40, '2': 35, '3': 30, '4': 25, '5': 20, '6': 15,
            'Specialty': 10, 'ST': 10
        }
        score += tier_scores.get(coverage.tier, 10)
        
        # Utilization management
        if not coverage.prior_auth:
            score += 20
        if not coverage.step_therapy:
            score += 20
        if not coverage.quantity_limit:
            score += 10
        
        # Cost scoring (using retail preferred as reference)
        if coverage.cost_type == 'copay':
            if coverage.retail_preferred_cost < 50:
                score += 10
            elif coverage.retail_preferred_cost < 100:
                score += 5
        elif coverage.cost_type == 'coinsurance':
            if coverage.retail_preferred_cost < 25:
                score += 10
            elif coverage.retail_preferred_cost < 33:
                score += 5
        
        return min(score, 100.0)
    
    def extract_coverage(self) -> List[CoverageAnalysis]:
        """
        Main extraction method
        
        Returns: List of CoverageAnalysis records for all GLP-1s across all plans
        """
        print("Starting GLP-1 coverage extraction...")
        
        # Load all data files
        print("Loading formulary data...")
        formulary_records = self.parse_formulary_file(
            self.data_dir / "basic_drugs_formulary.txt"
        )
        print(f"  Found {len(formulary_records)} GLP-1 formulary records")
        
        print("Loading cost data...")
        cost_records = self.parse_cost_file(
            self.data_dir / "beneficiary_cost.txt"
        )
        print(f"  Loaded {len(cost_records)} cost records")
        
        print("Loading plan information...")
        plan_info = self.parse_plan_info_file(
            self.data_dir / "plan_information.txt"
        )
        print(f"  Loaded {len(plan_info)} plans")
        
        # Build cost lookup: (contract_id, plan_id, tier) -> cost record
        cost_lookup = {}
        for cost in cost_records:
            key = (cost.contract_id, cost.plan_id, cost.tier)
            cost_lookup[key] = cost
        
        # Process coverage
        coverage_list = []
        
        for form_rec in formulary_records:
            # Get plan info
            plan_key = (form_rec.contract_id, form_rec.plan_id)
            plan = plan_info.get(plan_key)
            
            if not plan:
                continue  # Skip if plan info not found
            
            # Get cost info
            cost_key = (form_rec.contract_id, form_rec.plan_id, form_rec.tier)
            cost = cost_lookup.get(cost_key)
            
            # Get product
            product_name = self.ndc_to_product.get(form_rec.ndc)
            if not product_name:
                continue
            
            product = self.products[product_name]
            
            # Build coverage analysis
            coverage = CoverageAnalysis(
                contract_id=form_rec.contract_id,
                plan_id=form_rec.plan_id,
                plan_name=plan.plan_name,
                plan_type=plan.plan_type,
                organization_name=plan.organization_name,
                product_name=product.name,
                molecule=product.molecule,
                indication=product.indication,
                covered=True,
                tier=form_rec.tier,
                prior_auth=form_rec.prior_auth,
                step_therapy=form_rec.step_therapy,
                quantity_limit=form_rec.quantity_limit,
                cost_type=cost.cost_type if cost else 'unknown',
                retail_preferred_cost=cost.retail_preferred_cost if cost else 0.0,
                retail_standard_cost=cost.retail_standard_cost if cost else 0.0,
                mail_order_cost=cost.mail_order_cost if cost else 0.0,
                access_score=0.0  # Calculate below
            )
            
            # Calculate access score
            coverage.access_score = self.calculate_access_score(coverage)
            
            coverage_list.append(coverage)
        
        print(f"\nExtracted {len(coverage_list)} coverage records")
        
        return coverage_list
    
    def generate_summary_stats(self, coverage_list: List[CoverageAnalysis]) -> Dict:
        """Generate summary statistics"""
        
        stats = {
            'total_records': len(coverage_list),
            'unique_plans': len(set((c.contract_id, c.plan_id) for c in coverage_list)),
            'by_product': {},
            'by_indication': {},
            'by_molecule': {},
            'administrative_friction': {
                'prior_auth_pct': 0,
                'step_therapy_pct': 0,
                'quantity_limit_pct': 0
            },
            'tier_distribution': defaultdict(int),
            'average_access_score': 0.0
        }
        
        if not coverage_list:
            return stats
        
        # By product
        for product_name in self.products.keys():
            product_records = [c for c in coverage_list if c.product_name == product_name]
            stats['by_product'][product_name] = {
                'total_plans': len(set((c.contract_id, c.plan_id) for c in product_records)),
                'avg_access_score': sum(c.access_score for c in product_records) / len(product_records) if product_records else 0,
                'pa_rate': sum(1 for c in product_records if c.prior_auth) / len(product_records) * 100 if product_records else 0,
                'st_rate': sum(1 for c in product_records if c.step_therapy) / len(product_records) * 100 if product_records else 0
            }
        
        # Administrative friction
        stats['administrative_friction']['prior_auth_pct'] = sum(1 for c in coverage_list if c.prior_auth) / len(coverage_list) * 100
        stats['administrative_friction']['step_therapy_pct'] = sum(1 for c in coverage_list if c.step_therapy) / len(coverage_list) * 100
        stats['administrative_friction']['quantity_limit_pct'] = sum(1 for c in coverage_list if c.quantity_limit) / len(coverage_list) * 100
        
        # Tier distribution
        for c in coverage_list:
            stats['tier_distribution'][c.tier] += 1
        
        # Average access score
        stats['average_access_score'] = sum(c.access_score for c in coverage_list) / len(coverage_list)
        
        return stats


def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_glp1_coverage.py <data_directory>")
        print("\nExpected files in data directory:")
        print("  - basic_drugs_formulary.txt")
        print("  - beneficiary_cost.txt")
        print("  - plan_information.txt")
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    
    if not data_dir.exists():
        print(f"Error: Directory not found: {data_dir}")
        sys.exit(1)
    
    # Run extraction
    extractor = GLP1CoverageExtractor(data_dir)
    coverage_list = extractor.extract_coverage()
    
    # Generate stats
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    stats = extractor.generate_summary_stats(coverage_list)
    
    print(f"\nTotal Coverage Records: {stats['total_records']}")
    print(f"Unique Plans: {stats['unique_plans']}")
    print(f"Average Access Score: {stats['average_access_score']:.1f}/100")
    
    print("\n--- By Product ---")
    for product, data in stats['by_product'].items():
        print(f"{product}:")
        print(f"  Plans Covering: {data['total_plans']}")
        print(f"  Avg Access Score: {data['avg_access_score']:.1f}/100")
        print(f"  PA Rate: {data['pa_rate']:.1f}%")
        print(f"  ST Rate: {data['st_rate']:.1f}%")
    
    print("\n--- Administrative Friction (Overall) ---")
    print(f"Prior Authorization: {stats['administrative_friction']['prior_auth_pct']:.1f}%")
    print(f"Step Therapy: {stats['administrative_friction']['step_therapy_pct']:.1f}%")
    print(f"Quantity Limits: {stats['administrative_friction']['quantity_limit_pct']:.1f}%")
    
    print("\n--- Tier Distribution ---")
    for tier, count in sorted(stats['tier_distribution'].items()):
        pct = count / stats['total_records'] * 100
        print(f"Tier {tier}: {count} ({pct:.1f}%)")
    
    # Export to CSV
    output_file = data_dir / "glp1_coverage_analysis.csv"
    print(f"\nExporting detailed results to: {output_file}")
    
    with open(output_file, 'w', newline='') as f:
        if coverage_list:
            fieldnames = list(asdict(coverage_list[0]).keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for coverage in coverage_list:
                writer.writerow(asdict(coverage))
    
    # Export summary stats to JSON
    stats_file = data_dir / "glp1_summary_stats.json"
    with open(stats_file, 'w') as f:
        # Convert defaultdict to regular dict for JSON serialization
        stats_copy = dict(stats)
        stats_copy['tier_distribution'] = dict(stats['tier_distribution'])
        json.dump(stats_copy, f, indent=2)
    
    print(f"Summary statistics exported to: {stats_file}")
    print("\nExtraction complete!")


if __name__ == "__main__":
    main()
