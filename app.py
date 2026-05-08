import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Asset Sale Timing under CGT Reform", layout="wide")

# --- TITLE ---
st.title("Asset Sale Timing under CGT Reform")


# =====================================================
# INTRODUCTION (PURPOSE + MODEL OVERVIEW)
# =====================================================

st.markdown("""
### About this tool

Australia is considering changes to its Capital Gains Tax (CGT) regime, including proposals to replace the current CGT discount with inflation indexation.The proposed commencement date is currently expected to be 1 July 2026, though implementation details and transitional arrangements remain uncertain.This tool helps users explore how policy timing, growth, inflation, and discounting interact when evaluating asset sale timing decisions. 

### How the model works

The model compares after-tax outcomes across different selling times under a range of economic and policy assumptions.

For each possible selling year, it:

- Projects the future value of the asset from its current estimated market value using the assumed growth rate  
- Estimates total capital gains relative to the original purchase price  
- Applies different tax treatments depending on how long the asset is held under the current and proposed CGT systems, spliting gains between the current and proposed systems according to the proportion of total holding time spent under each regime. In particular, the model approximates a prospective transition approach in which inflation adjustment applies only to the portion of gains allocated to the new regime period. 
- Calculates after-tax proceeds  
- Converts those proceeds into present value terms using a discount rate  

The model then compares outcomes across selling times to illustrate how timing affects estimated after-tax value under the assumptions provided.The transition approach modelled here is illustrative only and is based on publicly reported proposals regarding time-based apportionment between CGT systems.


""")



# =====================================================
# INPUTS
# =====================================================

st.sidebar.header("Inputs")

purchase_price = st.sidebar.slider("Original Purchase Price ($)", 100000, 2000000, 800000)

current_market_value = st.sidebar.slider("Current Estimated Market Value ($)", 100000, 5000000, 1200000)

years_already_held = st.sidebar.slider("Years Already Held", 0, 40, 10)

tax_rate = st.sidebar.slider("Tax Rate (%)", 0, 50, 45) / 100
growth_rate = st.sidebar.slider("Expected Future Price Growth (yearly average) (%)", 0, 10, 5) / 100
inflation_rate = st.sidebar.slider("Expected Future Inflation (yearly average) (%)", 0, 10, 3) / 100
discount_rate = st.sidebar.slider("Discount Rate (yearly average) (%)", 0, 10, 5) / 100

sell_year = st.sidebar.slider("Years until Sale", 1, 40, 10)

#st.sidebar.caption("Measured from today, not from the policy commencement date.")

policy_date = st.sidebar.date_input(   "Expected Indexation Policy Commencement Date", datetime.date(2026, 7, 1))

today = datetime.date.today()

days_until_policy = (policy_date - today).days

policy_start = max(days_until_policy / 365, 0)


# =====================================================
# FUNCTIONS
# =====================================================

def cgt_current_growth(purchase_price, tax_rate, growth_rate, years):
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

    # Apportion gain by time
    gain_old_system = total_gain * (years_old_system / total_years)
    gain_new_system = total_gain * (years_new_system / total_years)

    # OLD SYSTEM TAX
    taxable_old = 0.5 * gain_old_system

    # NEW SYSTEM TAX (indexation)
    indexed_portion_cost = purchase_price * (
        years_new_system / total_years
    ) * ((1 + inflation_rate) ** years_new_system)

    taxable_new = max(
        gain_new_system - indexed_portion_cost,
        0
    )

    # Total tax
    total_taxable = taxable_old + taxable_new
    tax = total_taxable * tax_rate

    return tax, sale_price


def calculate_after_tax_npv(year):
    tax, sale_price = cgt_time_apportionment(purchase_price, current_market_value, tax_rate,inflation_rate,growth_rate, year,  years_already_held, policy_start)    
    after_tax = sale_price - tax
    npv = after_tax / ((1 + discount_rate) ** year)
    
    return npv, tax, sale_price

# =====================================================
# CURRENT SELECTION
# =====================================================

npv, tax, sale_price = calculate_after_tax_npv(sell_year)

# =====================================================
# SCENARIO ANALYSIS (OPTIMISATION)
# =====================================================

years_range = list(range(1, 41))

npv_values = []
tax_values = []
wealth_values = []

for y in years_range:
    n, t, sale_price = calculate_after_tax_npv(y)
    npv_values.append(n)
    tax_values.append(t)


    after_tax_wealth = sale_price - t
    wealth_values.append(after_tax_wealth)
    

best_year = years_range[npv_values.index(max(npv_values))]
best_npv = max(npv_values)


# =====================================================
# COMPARISON OF SELLING TIMINGS
# =====================================================

st.subheader("Comparison of Selling Timings")

st.markdown("""
This section compares the selected selling time with the timing that produces the highest estimated present-value outcome under the assumptions provided.
""")

# -----------------------------------------------------
# Main comparison cards
# -----------------------------------------------------

comparison_data = {
    "Metric": [
        "Years Until Sale",
        "Estimated Tax Liability",
        "Present Value of After-Tax Wealth"
    ],
    "Selected Timing Scenario": [
        f"{sell_year}",
        f"${tax:,.0f}",
        f"${npv:,.0f}"
    ],
    "Highest Present-Value Scenario": [
        f"{best_year}",
        f"${tax_values[years_range.index(best_year)]:,.0f}",
        f"${best_npv:,.0f}"
    ]
}

#st.table(comparison_data)

#st.dataframe( comparison_df, hide_index=True, use_container_width=True)

st.markdown(f"""
| Metric | Selected Sale Timing | Highest Present-Value Timing |
|---|---:|---:|
| Years Until Sale | {sell_year} | {best_year} |
| Estimated Tax Liability | ${tax:,.0f} | ${tax_values[years_range.index(best_year)]:,.0f} |
| Present Value of After-Tax Wealth | ${npv:,.0f} | ${best_npv:,.0f} |
""")

# -----------------------------------------------------
# Difference summary
# -----------------------------------------------------

st.markdown("---")

difference = best_npv - npv

col3, col4 = st.columns([1, 2])

with col3:

    st.metric(
        "Difference in Estimated Present Value",
        f"${difference:,.0f}"
    )

with col4:

    if difference > 0:

        st.info(
            f"""
            Under the current assumptions, an alternative selling time produces a higher estimated present-value outcome.

            The difference is primarily driven by the interaction between:
            - expected asset growth
            - tax treatment
            - discounting over time
            """
        )

    else:

        st.success(
            """
            Under the current assumptions, the selected timing produces an outcome consistent with the highest estimated present-value result.
            """
        )

# =====================================================
# 🧠 DYNAMIC EXPLANATION (SMART BUT SAFE)
# =====================================================

st.markdown("### Interpretation")

if discount_rate > growth_rate:
    st.write(
        "This outcome is primarily driven by the discount rate exceeding the expected growth rate, which reduces the present value of waiting."
    )
elif growth_rate > discount_rate:
    st.write(
        "This outcome is influenced by expected growth exceeding the discount rate, increasing the value of holding the asset for longer."
    )
else:
    st.write(
        "This outcome reflects a balance between growth and discounting, where timing effects become more sensitive to tax treatment."
    )

if inflation_rate > growth_rate:
    st.write(
        "Higher inflation relative to growth reduces real gains, which limits taxable gains under indexation."
    )
elif growth_rate > inflation_rate:
    st.write(
        "Positive real growth results in taxable gains even under indexation, affecting the relative tax outcomes."
    )

# Number formatter for charts
def currency_formatter(x, pos):
    return f'${x:,.0f}'

# =====================================================
# AFTER-TAX WEALTH CHART
# =====================================================

st.markdown("---")
st.subheader("How After-Tax Wealth Changes with Selling Time")

st.markdown("""
This chart shows estimated after-tax proceeds at the time of sale together with estimated tax payable.
""")

fig1, ax1 = plt.subplots(figsize=(10, 5))

# Wealth line
ax1.plot(
    years_range,
    wealth_values,
    linewidth=3,
    label="After-tax wealth"
)

ax1.set_xlabel("Years")
ax1.set_ylabel("After-tax wealth ($)")
ax1.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

# Secondary axis for tax
ax1b = ax1.twinx()

ax1b.plot(
    years_range,
    tax_values,
    linestyle="--",
    linewidth=2,
    label="Estimated tax liability"
)

ax1b.set_ylabel("Estimated tax liability ($)")
ax1b.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

# Policy change marker
ax1.axvline(
    policy_start,
    linestyle=":",
    linewidth=2,
    label="Policy change timing"
)

# Styling


ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

ax1b.spines['top'].set_visible(False)

ax1.tick_params(axis='both', which='major', labelsize=10)
ax1b.tick_params(axis='both', which='major', labelsize=10)

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1b.get_legend_handles_labels()

ax1.legend(
    lines1 + lines2,
    labels1 + labels2,
    frameon=False
)

st.pyplot(fig1)

# =====================================================
# PRESENT VALUE CHART
# =====================================================

st.markdown("---")
st.subheader("How Present Value of After-Tax Wealth Changes with Selling Time")

st.markdown("""
This chart converts future after-tax proceeds into today's dollars using the selected discount rate.
""")

fig2, ax2 = plt.subplots(figsize=(10, 5))

# NPV line
ax2.plot(
    years_range,
    npv_values,
    linewidth=3,
    label="NPV of after-tax wealth"
)

# Best scenario
ax2.scatter(
    best_year,
    best_npv,
    s=120,
    label="Highest value scenario"
)

# Policy marker
ax2.axvline(
    policy_start,
    linestyle=":",
    linewidth=2,
    label="Policy change timing"
)

ax2.set_xlabel("Years")
ax2.set_ylabel("NPV ($)")
ax2.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

# Secondary axis for tax
ax2b = ax2.twinx()

ax2b.plot(
    years_range,
    tax_values,
    linestyle="--",
    linewidth=2,
    label="Estimated tax liability"
)

ax2b.set_ylabel("Estimated tax liability ($)")
ax2b.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

# Styling

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

ax2b.spines['top'].set_visible(False)

ax2.tick_params(axis='both', which='major', labelsize=10)
ax2b.tick_params(axis='both', which='major', labelsize=10)



# Combined legend
lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2b.get_legend_handles_labels()

ax2.legend(
    lines1 + lines2,
    labels1 + labels2,
    frameon=False
)

st.pyplot(fig2)



# =====================================================
# GOVERNMENT REVENUE VIEW
# =====================================================

st.markdown("---")
st.subheader("Government Revenue Comparison")

st.markdown("""
This section illustrates how tax collected differs across systems.

It is provided for context and does not affect the scenario comparison above.
""")

tax_current_list = []
tax_index_list = []

for y in years_range:
    t_current, _ = cgt_current_growth(purchase_price, tax_rate, growth_rate, y)
    t_index, _ = cgt_time_apportionment(purchase_price, current_market_value, tax_rate, inflation_rate, growth_rate, y, years_already_held, policy_start)
    
    tax_current_list.append(t_current)
    tax_index_list.append(t_index)

fig3, ax3 = plt.subplots(figsize=(10, 5))

# Current system line
ax3.plot(
    years_range,
    tax_current_list,
    linestyle="--",
    linewidth=2.5,
    label="Current System"
)

# Indexation line
ax3.plot(
    years_range,
    tax_index_list,
    linewidth=3,
    label="Indexation / Transition Model"
)

# Policy marker
ax3.axvline(
    policy_start,
    linestyle=":",
    linewidth=2,
    label="Policy commencement"
)

# Labels
ax3.set_xlabel("Years Until Sale")
ax3.set_ylabel("Estimated Tax Collected ($)")

# Clean formatting
ax3.yaxis.set_major_formatter(FuncFormatter(currency_formatter))

# Styling
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

ax3.tick_params(axis='both', which='major', labelsize=10)

# Legend
ax3.legend(frameon=False)

st.pyplot(fig3)

tax_current_selected, _ = cgt_current_growth(purchase_price, tax_rate, growth_rate, sell_year)
tax_index_selected, _ = cgt_time_apportionment(
    purchase_price,
    current_market_value,
    tax_rate,
    inflation_rate,
    growth_rate,
    sell_year,
    years_already_held,
    policy_start
)

tax_difference = tax_current_selected - tax_index_selected

st.metric("Difference in tax collected (selected year)", f"${tax_difference:,.0f}")

# =====================================================
# UNDERSTANDING INDEXATION
# =====================================================

st.markdown("---")
st.subheader("Understanding Inflation Indexation")

st.markdown("""
Under an indexation system, the original purchase price is adjusted over time to reflect inflation.

Only gains above the inflation-adjusted cost base are treated as real capital gains and taxed accordingly.

This illustrative chart shows how an inflation-adjusted cost base can evolve relative to projected market value over time.
""")

# Example years
years_demo = list(range(0, 21))

# Example projected market values
market_values_demo = [
    purchase_price * ((1 + growth_rate) ** y)
    for y in years_demo
]

# Example indexed cost base
indexed_cost_demo = [
    purchase_price * ((1 + inflation_rate) ** y)
    for y in years_demo
]

# Create chart
fig3, ax3 = plt.subplots(figsize=(10, 5))

# Market value line
ax3.plot(
    years_demo,
    market_values_demo,
    linestyle="--",
    linewidth=2,
    label="Projected Market Value"
)

# Indexed cost base line
ax3.plot(
    years_demo,
    indexed_cost_demo,
    linewidth=3,
    label="Inflation-Adjusted Cost Base"
)

# Inflation area
ax3.fill_between(
    years_demo,
    purchase_price,
    indexed_cost_demo,
    alpha=0.2,
    label="Inflation Adjustment"
)

# Labels
ax3.set_xlabel("Years Held")
ax3.set_ylabel("Value ($)")

# Styling
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

ax3.tick_params(axis='both', which='major', labelsize=10)

# Legend
ax3.legend(frameon=False)

st.pyplot(fig3)

st.caption("""
Illustrative example only. The transition model used elsewhere in this tool applies a simplified time-apportionment approach rather than full retrospective indexation.
""")




# =====================================================
# EXPLANATION SECTION (END)
# =====================================================

st.markdown("---")
st.subheader("Model Explanation")

st.markdown("""
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