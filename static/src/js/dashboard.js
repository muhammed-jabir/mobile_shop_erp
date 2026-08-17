/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class MobileShopDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({ data: null });
        this.stockChartRef = useRef("stockChart");
        this.trendChartRef = useRef("trendChart");

        onWillStart(async () => {
          this.state.data = await this.orm.call(
                "mobile.shop.dashboard",
                "get_dashboard_data",
                [[]]
            );
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    renderCharts() {
        const data = this.state.data;
        if (!data) {
            return;
        }

        new Chart(this.stockChartRef.el, {
            type: "doughnut",
            data: {
                labels: ["Available", "Sold", "Under Repair", "Returned"],
                datasets: [{
                    data: [
                        data.stock_counts.available,
                        data.stock_counts.sold,
                        data.stock_counts.repair,
                        data.stock_counts.returned,
                    ],
                    backgroundColor: ["#28a745", "#dc3545", "#ffc107", "#6c757d"],
                }],
            },
        });

        new Chart(this.trendChartRef.el, {
            type: "line",
            data: {
                labels: data.trend.map((d) => d.date),
                datasets: [{
                    label: "Daily Sales",
                    data: data.trend.map((d) => d.total),
                    borderColor: "#875A7B",
                    backgroundColor: "rgba(135, 90, 123, 0.2)",
                    tension: 0.3,
                    fill: true,
                }],
            },
        });
    }
}

MobileShopDashboard.template = "mobile_shop_erp.Dashboard";

registry.category("actions").add("mobile_shop_dashboard", MobileShopDashboard);