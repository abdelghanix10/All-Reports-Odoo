# All Reports Odoo Module

**All Reports** is a custom Odoo 18 module that provides a consolidated dashboard for monitoring Point of Sale (POS) sessions, Manufacturing (Production), and Inventory Losses for a specific date.

## Features

### 1. Dashboard Overview

- **Date Filter**: Easily select a specific date to view reports. Defaults to the current date.
- **Tabbed Interface**: Navigate between Dashboard summary, Sessions, Production, and Lost Products.

### 2. POS Sessions Report

- **Session List**: Displays all POS sessions opened on the selected date.
- **Financials**: Shows Opening Balance, Closing Balance, Difference, and Total Sales.
- **Sales Breakdown**: Expandable accordion for each session showing sales grouped by POS Category.
- **Pagination**: Navigate through sessions easily with built-in pagination.
- **Currency Formatting**: All monetary values are formatted with "DH" and 2 decimal places.

### 3. Production Report

- **Aggregated Data**: Lists all manufactured products for the day.
- **Consolidated Quantities**: Merges multiple production moves for the same product into a single row.
- **Status Tracking**: Displays the status of production moves.

### 4. Lost Products & Analysis

- **Production vs Sales Comparison**: A powerful table that compares the quantity of products produced against the quantity sold in POS sessions.
  - Helps identify discrepancies between manufacturing output and actual sales.
  - Highlights differences in green (positive) or red (negative).
- **Lost Products Table**: Tracks inventory adjustments (lost products).
  - **Aggregated Quantities**: Merges multiple adjustments for the same product.
  - **Total Value Calculation**: Calculates the total value of lost stock based on the product's Sales Price (`Qty * Sales Price`).
  - **Status**: Shows the status of the inventory moves (e.g., Done).

## Technical Details

- **Odoo Version**: 18.0
- **Dependencies**: `point_of_sale`, `mrp`, `stock`, `web`
- **Architecture**:
  - **Frontend**: Built using the Odoo Web Library (OWL) framework.
  - **Backend**: Uses a `TransientModel` (`all_reports.dashboard`) to fetch and aggregate data efficiently.
  - **Security**: Includes proper access rights for the dashboard model.

## Installation

1.  Clone this repository into your Odoo addons path.
2.  Update your Odoo App List.
3.  Search for "All Reports" and click **Activate**.

## Usage

1.  Click on the **All Reports** menu item in the main Odoo app switcher.
2.  Select a date using the date picker at the top right.
3.  Switch between tabs to view detailed reports."
