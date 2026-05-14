import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Investor Incentives under CGT Reform", layout="wide")

# --- TITLE ---
st.title("Investor Incentives under CGT Reform")


# =====================================================
# INTRODUCTION (PURPOSE + MODEL OVERVIEW)
# =====================================================

st.markdown("""


### What does this tool do?  

This tool is designed to help investors explore how the proposed CGT reforms may affect incentives to sell assets before or after 1 July 2027 under different economic assumptions.

### Reform

On 12 May 2026, as part of the 2026–27 Federal Budget, the Australian Government announced it would reform capital gains tax (CGT) arrangements.These changes, which are intended to apply from 1 July 2027, will replace the 50% CGT discount 
for individuals, trusts and partnerships with cost base indexation and a 30% minimum tax rate on real (TBC) capital gains.

Assets owned prior to 1 July 2027 and sold after 1 July 2027 will be treated under current arrangements on gains made prior to this date, 
and under the new arrangements for gains made after this date. A key component of an indexation system is determining the cost base from which indexation begins. 
For assets purchased after 1 July 2027, this would generally be the original purchase price. 
For assets purchased before the policy starts, the relevant starting cost base may need to be estimated under the transition arrangements. 

To determine an asset’s value at 1 July 2027, investors can either: 

• seek a valuation of the asset as at 1 July 2027; or  
• use a specified apportionment formula that estimates the asset’s value on 1 July 2027, based on its growth rate over the asset’s holding period.  


### How to use this tool

Use the input panel on the left-hand side of the screen to:

1. Enter information about the asset, including its original purchase price, current estimated market value and purchase date  
2. Select a potential pre-reform sale date and a post-reform sale date to compare different selling scenarios  
3. Adjust economic assumptions such as future asset growth, inflation and discount rates  
4. Compare estimated taxable capital gains, tax liabilities and after-tax outcomes under the current CGT system and the proposed transition indexation model  

The charts and scenario comparison table illustrate how the proposed reforms may change incentives to sell assets before or after 1 July 2027.

""")

# =====================================================
# INPUTS
# =====================================================

st.sidebar.header("Asset Information")

purchase_price = st.sidebar.slider("Original Purchase Price ($)", 100000, 2000000, 800000)

current_market_value = st.sidebar.slider(
    "Current Estimated Market Value ($)",
    min_value=100000,
    max_value=10000000,
    value=1200000,
    step=20000
)

purchase_date = st.sidebar.date_input(
    "Asset Purchase Date",
    datetime.date(2015, 1, 1)
)

st.sidebar.header("Tax Settings")

tax_rate = st.sidebar.slider("Marginal Tax Rate under the current system (%)", 0, 50, 45) / 100

st.sidebar.header("Sale Timing Scenarios")

pre_reform_sale_date = st.sidebar.date_input(
    "Pre-Reform Sale Date",
    datetime.date.today(),
    min_value=datetime.date.today(),
    max_value=datetime.date(2027, 6, 30)
)

sale_date = st.sidebar.date_input(
    "Post-Reform Sale Date",
    min_value=datetime.date(2027, 7, 1)
)

policy_date = datetime.date(2027, 7, 1)

minimum_cgt_rate = 0.30

if purchase_date >= policy_date:
    st.warning(
        "This model is designed for assets acquired before the commencement of the reform."
    )
    st.stop()

today = datetime.date.today()

days_until_policy = (policy_date - today).days

policy_start = max(days_until_policy / 365, 0)



st.sidebar.header("Economic Assumptions")

growth_rate = st.sidebar.slider(
    "Expected Long-Run Nominal Asset Growth (%)",
    min_value=0.0,
    max_value=10.0,
    value=5.0,
    step=0.1
) / 100

inflation_rate = st.sidebar.slider("Expected Future Inflation (yearly average) (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.1) / 100

discount_rate = st.sidebar.slider("Discount Rate (yearly average) (%)", 0, 10, 5) / 100



# -----------------------------------------------------
# Time calculations
# -----------------------------------------------------

today = datetime.date.today()

years_already_held = max(
    (today - purchase_date).days / 365,
    0
)

years_future = max(
    (sale_date - today).days / 365,
    0
)

total_holding_years = years_already_held + years_future



# =====================================================
# FUNCTIONS
# =====================================================

def cgt_current_growth(purchase_price,current_market_value,tax_rate, growth_rate, years):

    sale_price = current_market_value * (1 + growth_rate) ** years
    gain = sale_price - purchase_price
    taxable_gain = 0.5 * gain
    tax = taxable_gain * tax_rate
    return tax, sale_price

def cgt_time_apportionment(purchase_price,current_market_value,tax_rate,inflation_rate,growth_rate, years_future, years_already_held,policy_start):

    # Project future sale price
    sale_price = current_market_value * (1 + growth_rate) ** years_future

    # Total capital gain
    total_gain = sale_price - purchase_price

    # Total holding period at sale
    total_years = years_already_held + years_future

    # Years under old system
    years_old_system = years_already_held + min(years_future, policy_start)

    # Years under new system
    years_new_system = max(years_future - policy_start, 0)

    # -----------------------------------------------------
    # Apportion sale proceeds and cost base
    # -----------------------------------------------------

    sale_old_system = sale_price * (years_old_system / total_years)

    sale_new_system = sale_price * (years_new_system / total_years)

    cost_old_system = purchase_price * (
    years_old_system / total_years)

    cost_new_system = purchase_price * (
    years_new_system / total_years)

    # -----------------------------------------------------
    # OLD SYSTEM
    # -----------------------------------------------------

    gain_old_system = (sale_old_system - cost_old_system)

    taxable_old = max(0.5 * gain_old_system, 0)

   # -----------------------------------------------------
   # NEW SYSTEM (INDEXATION)
   # -----------------------------------------------------

    indexed_cost_new = cost_new_system * ((1 + inflation_rate) ** years_new_system)

    taxable_new = max( sale_new_system - indexed_cost_new, 0)   


    # Tax under old system
    tax_old = taxable_old * tax_rate

    # Apply 30% minimum tax rate under new system
    effective_new_tax_rate = max(
    tax_rate,
    minimum_cgt_rate
    )

   # Tax under new system
    tax_new = taxable_new * effective_new_tax_rate

    # Combined tax
    tax = tax_old + tax_new   

    return tax, sale_price


def calculate_after_tax_npv(year):
    tax, sale_price = cgt_time_apportionment(purchase_price, current_market_value, tax_rate,inflation_rate,growth_rate, year,  years_already_held, policy_start)    
    after_tax = sale_price - tax
    npv = after_tax / ((1 + discount_rate) ** year)
    
    return npv, tax, sale_price

# =====================================================
# CURRENT SELECTION
# =====================================================

npv, tax, sale_price = calculate_after_tax_npv(years_future)
selected_sale_price = sale_price


# =====================================================
# SCENARIO ANALYSIS
# =====================================================

# Create a cleaner chart horizon
# Always show at least 2 years

chart_start = min(pre_reform_sale_date, sale_date)

minimum_chart_end = (
    chart_start + datetime.timedelta(days=730)
)

chart_end = max(
    sale_date,
    minimum_chart_end
)

# Generate monthly chart dates
chart_dates = []

current_date = chart_start

while current_date <= chart_end:
    chart_dates.append(current_date)
    current_date += datetime.timedelta(days=30)

# Convert chart dates into year fractions
chart_years = [
    max((d - today).days / 365, 0)
    for d in chart_dates
]

# Store results
npv_values = []
tax_values = []
sale_price_values = []
after_tax_values = []

# Calculate values across chart horizon
for y in chart_years:

    n, t, projected_sale_price = calculate_after_tax_npv(y)

    npv_values.append(n)
    tax_values.append(t)

    after_tax_sale_proceeds = (
        projected_sale_price - t
    )

    after_tax_values.append(after_tax_sale_proceeds)

    sale_price_values.append(projected_sale_price)


# -----------------------------------------------------
# Pre-reform sale scenario
# -----------------------------------------------------

pre_reform_years = max(
    (pre_reform_sale_date - today).days / 365,
    0
)

pre_reform_sale_date = (
    today + datetime.timedelta(days=int(pre_reform_years * 365))
)

pre_reform_npv, pre_reform_tax, pre_reform_sale_price = (
    calculate_after_tax_npv(pre_reform_years)
)

pre_reform_after_tax = (
    pre_reform_sale_price - pre_reform_tax
)



# =====================================================
# SCENARIO COMPARISON
# =====================================================

st.markdown("---")
st.subheader("Scenario Comparison")

st.markdown("""
This comparison illustrates how estimated outcomes may differ if an existing asset is sold before or after the commencement of the proposed CGT reform.
""")

# -----------------------------------------------------
# Pre-reform scenario
# -----------------------------------------------------

pre_reform_npv, pre_reform_tax, pre_reform_sale_price = (
    calculate_after_tax_npv(pre_reform_years)
)

pre_reform_after_tax = (
    pre_reform_sale_price - pre_reform_tax
)

# -----------------------------------------------------
# Selected scenario
# -----------------------------------------------------

selected_sale_price = sale_price

selected_after_tax = (
    selected_sale_price - tax
)


# =====================================================
# HEADLINE DIFFERENCE
# =====================================================

difference = (
    selected_after_tax - pre_reform_after_tax
)

if difference > 0:
    direction = "higher"
else:
    direction = "lower"

st.markdown(f"""
**Under the selected assumptions, estimated after-tax sale proceeds at the time of sale are approximately ${abs(difference):,.0f} {direction} if the asset is sold after the reform.**
""")



# -----------------------------------------------------
# Table
# -----------------------------------------------------

st.markdown(f"""
| Metric | Pre-Reform Sale | Post-Reform Sale |
|---|---:|---:|
| Sale Date | {pre_reform_sale_date.strftime("%d %b %Y")} | {sale_date.strftime("%d %b %Y")} |
| Expected Sale Price | ${pre_reform_sale_price:,.0f} | ${selected_sale_price:,.0f} |
| Estimated Tax | ${pre_reform_tax:,.0f} | ${tax:,.0f} |
| After-Tax Sale Proceeds | ${pre_reform_after_tax:,.0f} | ${selected_after_tax:,.0f} |
| Present Value of After-Tax Sale Proceeds | ${pre_reform_npv:,.0f} | ${npv:,.0f} |
""")


# -----------------------------------------------------
# Number formatter for charts
# -----------------------------------------------------

def currency_formatter(x, pos):
    return f'${x:,.0f}'


# =====================================================
# AFTER-TAX SALE PROCEEDS CHART
# =====================================================

st.markdown("---")
st.subheader("How After-Tax Sale Proceeds Change with Selling Time")

st.markdown("""
This chart shows estimated after-tax proceeds at the time of sale together with estimated tax payable.
""")

fig1, ax1 = plt.subplots(figsize=(10, 5))

# -----------------------------------------------------
# Main line
# -----------------------------------------------------

ax1.plot(
    chart_dates,
    after_tax_values,
    linewidth=3,
    label="After-tax sale proceeds"
)

# -----------------------------------------------------
# Scenario markers
# -----------------------------------------------------

# Pre-reform sale marker
ax1.scatter(
    pre_reform_sale_date,
    pre_reform_after_tax,
    s=80,
    zorder=5,
    label="Pre-reform sale"
)

# Post-reform sale marker
ax1.scatter(
    sale_date,
    selected_after_tax,
    s=80,
    zorder=5,
    label="Post-reform sale"
)

# -----------------------------------------------------
# Policy commencement marker
# -----------------------------------------------------

ax1.axvline(
    policy_date,
    linestyle=":",
    linewidth=2,
    label="Policy commencement"
)

# -----------------------------------------------------
# Axis formatting
# -----------------------------------------------------

ax1.set_xlabel("Sale Date")
ax1.set_ylabel("After-tax Sale Proceeds ($)")
ax1.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

# -----------------------------------------------------
# Secondary axis for tax
# -----------------------------------------------------

ax1b = ax1.twinx()

ax1b.plot(
    chart_dates,
    tax_values,
    linestyle="--",
    linewidth=2,
    label="Estimated tax liability"
)

ax1b.set_ylabel("Estimated tax liability ($)")
ax1b.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

# -----------------------------------------------------
# Styling
# -----------------------------------------------------

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

ax1b.spines['top'].set_visible(False)

ax1.tick_params(axis='both', which='major', labelsize=10)
ax1b.tick_params(axis='both', which='major', labelsize=10)

# -----------------------------------------------------
# Combined legend
# -----------------------------------------------------

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1b.get_legend_handles_labels()

ax1.legend(
    lines1 + lines2,
    labels1 + labels2,
    frameon=False
)

# Improve date formatting
fig1.autofmt_xdate()

st.pyplot(fig1)

# =====================================================
# PRESENT VALUE CHART
# =====================================================

st.markdown("---")
st.subheader("How Present Value of After-Tax Sale Proceeds Changes with Selling Time")

st.markdown("""
This chart converts future after-tax proceeds into today's dollars using the selected discount rate.
""")

fig2, ax2 = plt.subplots(figsize=(10, 5))

# -----------------------------------------------------
# Main NPV line
# -----------------------------------------------------

ax2.plot(
    chart_dates,
    npv_values,
    linewidth=3,
    label="Present value of after-tax sale proceeds"
)

# -----------------------------------------------------
# Scenario markers
# -----------------------------------------------------

# Pre-reform marker
ax2.scatter(
    pre_reform_sale_date,
    pre_reform_npv,
    s=80,
    zorder=5,
    label="_nolegend_"
)

# Post-reform marker
ax2.scatter(
    sale_date,
    npv,
    s=80,
    zorder=5,
    label="_nolegend_"
)

# -----------------------------------------------------
# Policy commencement marker
# -----------------------------------------------------

ax2.axvline(
    policy_date,
    linestyle=":",
    linewidth=2,
    label="Policy commencement"
)

# -----------------------------------------------------
# Axis formatting
# -----------------------------------------------------

ax2.set_xlabel("Sale Year")
ax2.set_ylabel("Present Value ($)")
ax2.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

# -----------------------------------------------------
# Secondary axis for tax
# -----------------------------------------------------

ax2b = ax2.twinx()

ax2b.plot(
    chart_dates,
    tax_values,
    linestyle="--",
    linewidth=2,
    label="Estimated tax liability"
)

ax2b.set_ylabel("Estimated tax liability ($)")
ax2b.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

# -----------------------------------------------------
# Styling
# -----------------------------------------------------

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

ax2b.spines['top'].set_visible(False)

ax2.tick_params(axis='both', which='major', labelsize=10)
ax2b.tick_params(axis='both', which='major', labelsize=10)

# -----------------------------------------------------
# Combined legend
# -----------------------------------------------------

lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2b.get_legend_handles_labels()

ax2.legend(
    lines1 + lines2,
    labels1 + labels2,
    frameon=False
)

# Improve date formatting
fig2.autofmt_xdate()

st.pyplot(fig2)


# =====================================================
# EXPLANATION SECTION (END)
# =====================================================

st.markdown("---")
st.subheader("Model Explanation")

st.markdown("""

### How the model works

The model compares after-tax outcomes across different selling times under a range of economic assumptions.

For each possible selling year, it:

- Projects the future value of the asset from its current estimated market value using the assumed future growth rate  
- Estimates total capital gains relative to the original purchase price  
- Applies different tax treatments depending on how long the asset is held under the current and proposed CGT systems  
- Uses a simplified time-based apportionment approach to split gains between the old and new regimes during the transition period  
- Calculates estimated after-tax proceeds  
- Converts those proceeds into present value terms using a discount rate  

The model then compares outcomes across different selling times to illustrate how timing assumptions affect estimated after-tax outcomes.


### Why outcomes differ across scenarios

Different selling times produce different outcomes because:

- Asset values evolve over time  
- Tax treatment may change depending on policy timing  
- Future proceeds are discounted back to present value  

---

### What is the discount rate?

The discount rate reflects how much future money is valued relative to today.

- Higher discount rate → future proceeds are worth less  
- Lower discount rate → future proceeds retain more value  

It plays a central role in comparing earlier versus later outcomes.
""")

# =====================================================
# DISCLAIMER
# =====================================================

st.markdown("---")
st.caption("""
This tool is provided for illustrative purposes only and is based on simplified assumptions.  
It does not constitute financial, tax, or investment advice.  
Users should seek professional advice before making financial decisions.
""")