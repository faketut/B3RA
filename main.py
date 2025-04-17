# Basel III Capital Adequacy Risk Dashboard - Python Implementation

import pandas as pd
import numpy as np
from scipy.stats import norm, lognorm

# Function to calculate Risk Weighted Assets
def calculate_rwa(portfolio_data):
    # Apply risk weights based on asset class and internal ratings
    portfolio_data['credit_rwa'] = portfolio_data['exposure_amount'] * portfolio_data['risk_weight']
    portfolio_data['market_rwa'] = portfolio_data['exposure_amount'] * portfolio_data['market_risk_factor']
    portfolio_data['op_rwa'] = portfolio_data['exposure_amount'] * portfolio_data['op_risk_factor']
    portfolio_data['total_rwa'] = portfolio_data['credit_rwa'] + portfolio_data['market_rwa'] + portfolio_data['op_rwa']
    
    return portfolio_data

# Function to calculate Basel III ratios
def calculate_basel_ratios(portfolio_data, tier1_capital, total_capital, hqla, expected_outflows, available_stable_funding, required_stable_funding):
    total_rwa = portfolio_data['total_rwa'].sum()
    
    # Capital Ratios
    tier1_ratio = tier1_capital / total_rwa * 100
    total_capital_ratio = total_capital / total_rwa * 100
    
    # Liquidity Ratios
    lcr = hqla / expected_outflows * 100
    nsfr = available_stable_funding / required_stable_funding * 100
    
    return {
        'tier1_ratio': tier1_ratio,
        'total_capital_ratio': total_capital_ratio,
        'lcr': lcr,
        'nsfr': nsfr,
        'total_rwa': total_rwa
    }

# Function to run stress tests
def run_stress_test(portfolio_data, tier1_capital, total_capital, hqla, expected_outflows, available_stable_funding, required_stable_funding, stress_scenario):
    # Apply stress scenarios to risk parameters
    if stress_scenario == "Mild Recession":
        portfolio_data['risk_weight'] = portfolio_data['risk_weight'] * 1.2
        portfolio_data['market_risk_factor'] = portfolio_data['market_risk_factor'] * 1.5
        portfolio_data['op_risk_factor'] = portfolio_data['op_risk_factor'] * 1.1
        hqla = hqla * 0.9
        expected_outflows = expected_outflows * 1.2
        available_stable_funding = available_stable_funding * 0.95
        required_stable_funding = required_stable_funding * 1.05
    elif stress_scenario == "Severe Recession":
        portfolio_data['risk_weight'] = portfolio_data['risk_weight'] * 1.5
        portfolio_data['market_risk_factor'] = portfolio_data['market_risk_factor'] * 2.0
        portfolio_data['op_risk_factor'] = portfolio_data['op_risk_factor'] * 1.3
        hqla = hqla * 0.75
        expected_outflows = expected_outflows * 1.5
        available_stable_funding = available_stable_funding * 0.85
        required_stable_funding = required_stable_funding * 1.2
    elif stress_scenario == "Financial Crisis":
        portfolio_data['risk_weight'] = portfolio_data['risk_weight'] * 2.0
        portfolio_data['market_risk_factor'] = portfolio_data['market_risk_factor'] * 3.0
        portfolio_data['op_risk_factor'] = portfolio_data['op_risk_factor'] * 1.5
        hqla = hqla * 0.6
        expected_outflows = expected_outflows * 2.0
        available_stable_funding = available_stable_funding * 0.7
        required_stable_funding = required_stable_funding * 1.4
    
    # Calculate RWA under stress
    stressed_portfolio = calculate_rwa(portfolio_data)
    
    # Calculate Basel ratios under stress
    stressed_ratios = calculate_basel_ratios(
        stressed_portfolio, 
        tier1_capital, 
        total_capital, 
        hqla, 
        expected_outflows, 
        available_stable_funding, 
        required_stable_funding
    )
    
    return {
        'portfolio': stressed_portfolio,
        'ratios': stressed_ratios
    }

# Generate synthetic portfolio data (for demo purposes)
def generate_synthetic_data(n = 100):
    asset_classes = ["Corporate Loans", "Retail Mortgages", "Sovereign Debt", "Commercial Real Estate", "Consumer Loans"]
    ratings = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
    
    data = pd.DataFrame({
        'asset_id': [f"ASSET{i}" for i in range(1, n + 1)],
        'asset_class': np.random.choice(asset_classes, n, replace=True),
        'internal_rating': np.random.choice(ratings, n, replace=True, p=[0.05, 0.1, 0.2, 0.3, 0.2, 0.1, 0.05]),
        'exposure_amount': np.round(lognorm.rvs(loc=np.log(1000000), s=1, size=n), 2),
        'probability_of_default': None,
        'risk_weight': None,
        'market_risk_factor': None,
        'op_risk_factor': None
    })
    
    # Assign PD based on ratings
    pd_map = {"AAA": 0.0001, "AA": 0.0005, "A": 0.001, "BBB": 0.003, "BB": 0.01, "B": 0.05, "CCC": 0.15}
    data['probability_of_default'] = data['internal_rating'].map(pd_map)
    
    # Assign risk weights based on asset class and rating
    data['risk_weight'] = 0.0  # Initialize risk_weight column
    for i in range(len(data)):
        if data['asset_class'][i] == "Sovereign Debt":
            if data['internal_rating'][i] in ["AAA", "AA", "A"]:
                data.loc[i, 'risk_weight'] = 0.0
            elif data['internal_rating'][i] == "BBB":
                data.loc[i, 'risk_weight'] = 0.2
            else:
                data.loc[i, 'risk_weight'] = 0.5
        elif data['asset_class'][i] == "Retail Mortgages":
            data.loc[i, 'risk_weight'] = 0.35
        elif data['asset_class'][i] == "Consumer Loans":
            data.loc[i, 'risk_weight'] = 0.75
        elif data['asset_class'][i] == "Corporate Loans":
            if data['internal_rating'][i] in ["AAA", "AA", "A"]:
                data.loc[i, 'risk_weight'] = 0.2
            elif data['internal_rating'][i] == "BBB":
                data.loc[i, 'risk_weight'] = 0.5
            elif data['internal_rating'][i] == "BB":
                data.loc[i, 'risk_weight'] = 1.0
            else:
                data.loc[i, 'risk_weight'] = 1.5
        elif data['asset_class'][i] == "Commercial Real Estate":
            data.loc[i, 'risk_weight'] = 1.0
    
    # Add market and operational risk factors
    data['market_risk_factor'] = np.where(data['asset_class'].isin(["Sovereign Debt", "Corporate Loans"]),
                                        np.random.uniform(0.05, 0.15, size=len(data)),
                                        np.random.uniform(0.01, 0.05, size=len(data)))
    
    data['op_risk_factor'] = np.where(data['asset_class'].isin(["Retail Mortgages", "Consumer Loans"]),
                                    np.random.uniform(0.08, 0.12, size=len(data)),
                                    np.random.uniform(0.05, 0.1, size=len(data)))
    
    return data

# Example usage:
if __name__ == '__main__':
    # Generate synthetic data
    portfolio_data = generate_synthetic_data(150)
    
    # Calculate RWA
    portfolio_data = calculate_rwa(portfolio_data)
    
    # Define Basel III parameters
    tier1_capital = 1000000000  # $1B
    total_capital = 1200000000  # $1.2B
    hqla = 800000000  # $800M
    expected_outflows = 600000000  # $600M
    available_stable_funding = 1500000000  # $1.5B
    required_stable_funding = 1200000000  # $1.2B
    
    # Calculate Basel III ratios
    basel_ratios = calculate_basel_ratios(
        portfolio_data, 
        tier1_capital, 
        total_capital, 
        hqla, 
        expected_outflows, 
        available_stable_funding, 
        required_stable_funding
    )
    
    print("Basel III Ratios:")
    for key, value in basel_ratios.items():
        print(f"{key}: {value}")
    
    # Run stress test
    stress_scenario = "Severe Recession"
    stress_results = run_stress_test(
        portfolio_data, 
        tier1_capital, 
        total_capital, 
        hqla, 
        expected_outflows, 
        available_stable_funding, 
        required_stable_funding,
        stress_scenario
    )
    
    print(f"\nStress Test Results ({stress_scenario}):")
    for key, value in stress_results['ratios'].items():
        print(f"{key}: {value}")
