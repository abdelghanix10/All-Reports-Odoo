/** @odoo-module */

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class AllReportsDashboard extends Component {
  setup() {
    this.orm = useService("orm");
    const today = new Date().toISOString().split("T")[0];
    this.state = useState({
      startDate: today,
      endDate: today,
      activeTab: "dashboard",
      data: {
        sessions: [],
        production: [],
        production_vs_sales: [],
        lost_products: [],
      },
      loading: true,
      sessionsPage: 1,
      sessionsPerPage: 5,
      expandedSessions: {},
    });

    onWillStart(async () => {
      await this.fetchData();
    });
  }

  async fetchData() {
    this.state.loading = true;
    // Reset pagination on new data fetch
    this.state.sessionsPage = 1;
    this.state.expandedSessions = {};

    try {
      const result = await this.orm.call(
        "all_reports.dashboard",
        "get_dashboard_data",
        [this.state.startDate, this.state.endDate]
      );
      this.state.data = result;
    } catch (e) {
      console.error("Error fetching data", e);
    } finally {
      this.state.loading = false;
    }
  }

  async onStartDateChange(ev) {
    this.state.startDate = ev.target.value;
    // Ensure endDate is not before startDate
    if (this.state.endDate < this.state.startDate) {
      this.state.endDate = this.state.startDate;
    }
    await this.fetchData();
  }

  async onEndDateChange(ev) {
    this.state.endDate = ev.target.value;
    // Ensure startDate is not after endDate
    if (this.state.startDate > this.state.endDate) {
      this.state.startDate = this.state.endDate;
    }
    await this.fetchData();
  }

  setTab(tab) {
    this.state.activeTab = tab;
  }

  // Pagination Helpers
  get paginatedSessions() {
    const start = (this.state.sessionsPage - 1) * this.state.sessionsPerPage;
    const end = start + this.state.sessionsPerPage;
    return this.state.data.sessions.slice(start, end);
  }

  get totalSessionPages() {
    return Math.ceil(
      this.state.data.sessions.length / this.state.sessionsPerPage
    );
  }

  nextPage() {
    if (this.state.sessionsPage < this.totalSessionPages) {
      this.state.sessionsPage++;
    }
  }

  prevPage() {
    if (this.state.sessionsPage > 1) {
      this.state.sessionsPage--;
    }
  }

  // Accordion Helper
  toggleSession(sessionId) {
    if (this.state.expandedSessions[sessionId]) {
      delete this.state.expandedSessions[sessionId];
    } else {
      this.state.expandedSessions[sessionId] = true;
    }
  }

  // Formatting Helper
  formatCurrency(amount) {
    if (amount === undefined || amount === null) return "0.00 DH";
    return (
      amount.toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }) + " DH"
    );
  }
}

AllReportsDashboard.template = "all_reports.Dashboard";

registry.category("actions").add("all_reports.dashboard", AllReportsDashboard);
