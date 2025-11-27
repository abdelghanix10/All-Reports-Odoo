/** @odoo-module */

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class AllReportsDashboard extends Component {
  setup() {
    this.orm = useService("orm");
    this.state = useState({
      date: new Date().toISOString().split("T")[0],
      activeTab: "dashboard",
      data: {
        sessions: [],
        production: [],
        lost_products: [],
        debug_logs: [],
      },
      loading: true,
    });

    onWillStart(async () => {
      await this.fetchData();
    });
  }

  async fetchData() {
    this.state.loading = true;
    try {
      const result = await this.orm.call(
        "all_reports.dashboard",
        "get_dashboard_data",
        [this.state.date]
      );
      this.state.data = result;
    } catch (e) {
      console.error("Error fetching data", e);
    } finally {
      this.state.loading = false;
    }
  }

  async onDateChange(ev) {
    this.state.date = ev.target.value;
    await this.fetchData();
  }

  setTab(tab) {
    this.state.activeTab = tab;
  }
}

AllReportsDashboard.template = "all_reports.Dashboard";

registry.category("actions").add("all_reports.dashboard", AllReportsDashboard);
