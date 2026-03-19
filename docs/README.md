    # Documentation

    This folder contains project-level documentation and analysis references.

    ## EDA Findings (From notebook/EDA.ipynb)

    The exploratory data analysis currently lives in the notebook and is summarized here for quick reference.

    ### Data Quality Snapshot

    - Initial profiling included missing value checks, duplicate checks, datatype inspection, and shape validation.
    - Postal code was removed during cleaning in notebook work where not needed for analysis.

    ### Sales Trend Analysis

    - 2018 shows the strongest revenue performance among the analyzed years.
    - A recurring month-level pattern appears where sales rise from July to August across years.
    - February shows notable peaks in later years (especially 2017 and 2018), indicating possible seasonality and/or stronger campaign effects.
    - Overall monthly sales fluctuate, but February and August repeatedly appear as high-performing months.

    ### Shipping Lag Trend Analysis

    - Average shipping lag varies moderately across years, with no persistent long-term worsening trend.
    - Most months stay within a relatively stable shipping-delay band, indicating consistent logistics performance.
    - A visible dip in lag appears around 2017 for several months, suggesting temporary efficiency improvement.
    - Some early and mid-year months show slightly higher lag, which may reflect workload or operational constraints.

    ### Regional and Segment Insights

    - Revenue distribution differs by region, with one region leading total sales in the grouped analysis.
    - Category and segment-level sales are uneven, with clear concentration in top-performing groups.
    - Customer concentration is visible in top states and cities, useful for geography-focused business targeting.

    ## Where To Keep EDA Trend Notes

    Recommended documentation split:

    - Keep short highlights in the root README for quick project overview.
    - Keep detailed analysis narrative and trend interpretation in this docs README.
    - Keep all plots, exploratory code, and iterative analysis in notebook/EDA.ipynb.

    This keeps onboarding simple while preserving full analytical context.
