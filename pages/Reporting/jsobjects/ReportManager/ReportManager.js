export default {
    // Current report state
    currentReport: 'all_orders',

    // Switch between different report types
    switchReport: (reportType) => {
      storeValue('currentReportType', reportType);
      storeValue('reportLoading', true);

      // Run appropriate query based on report type
      switch(reportType) {
        case 'all_orders':
          AllOrdersReport.run()
            .then(() => storeValue('reportLoading', false))
            .catch(() => {
              storeValue('reportLoading', false);
              showAlert('Failed to load All Orders report', 'error');
            });
          break;
        case 'daily_cash_flow':
          DailyCashFlowReport.run()
            .then(() => storeValue('reportLoading', false))
            .catch(() => {
              storeValue('reportLoading', false);
              showAlert('Failed to load Daily Cash Flow report', 'error');
            });
          break;
        case 'payment_analysis':
          PaymentAnalysisReport.run()
            .then(() => storeValue('reportLoading', false))
            .catch(() => {
              storeValue('reportLoading', false);
              showAlert('Failed to load Payment Analysis report', 'error');
            });
          break;
        case 'monthly_summary':
          MonthlyFinancialSummary.run()
            .then(() => storeValue('reportLoading', false))
            .catch(() => {
              storeValue('reportLoading', false);
              showAlert('Failed to load Monthly Summary report', 'error');
            });
          break;
        case 'business_metrics':
          BusinessMetricsDashboard.run()
            .then(() => storeValue('reportLoading', false))
            .catch(() => {
              storeValue('reportLoading', false);
              showAlert('Failed to load Business Metrics report', 'error');
            });
          break;
        case 'service_billing':
          ServiceBillingReport.run()
            .then(() => storeValue('reportLoading', false))
            .catch(() => {
              storeValue('reportLoading', false);
              showAlert('Failed to load Service Billing report', 'error');
            });
          break;
        default:
          storeValue('reportLoading', false);
          showAlert('Unknown report type selected', 'warning');
      }
    },

    // Refresh all reports
    refreshAllReports: () => {
      storeValue('reportLoading', true);

      const promises = [
        AllOrdersReport.run(),
        DailyCashFlowReport.run(),
        PaymentAnalysisReport.run(),
        MonthlyFinancialSummary.run(),
        BusinessMetricsDashboard.run(),
        ServiceBillingReport.run(),
        MostPopularProducts.run()
      ];

      Promise.all(promises)
        .then(() => {
          storeValue('reportLoading', false);
          showAlert('All reports refreshed successfully!', 'success');
        })
        .catch((error) => {
          storeValue('reportLoading', false);
          showAlert('Error refreshing reports: ' + error.message, 'error');
        });
    },

    // Refresh current report only
    refreshCurrentReport: () => {
      const currentType = ReportTypeSelect.selectedOptionValue || appsmith.store.currentReportType || 'all_orders';
      this.switchReport(currentType);
    },

    // Set quick date ranges with Bulgaria timezone
    setDateRange: (range) => {
      let startDate, endDate;
      // Force Bulgaria timezone and ensure we're working with local dates
      const today = moment().utc().add(3, 'hours'); // Bulgaria is UTC+3

      switch(range) {
        case 'today':
          startDate = today.clone().startOf('day');
          endDate = today.clone().endOf('day');
          break;
        case 'yesterday':
          startDate = today.clone().subtract(1, 'day').startOf('day');
          endDate = today.clone().subtract(1, 'day').endOf('day');
          break;
        case 'week':
          startDate = today.clone().subtract(7, 'days').startOf('day');
          endDate = today.clone().endOf('day');
          break;
        case 'month':
          startDate = today.clone().subtract(30, 'days').startOf('day');
          endDate = today.clone().endOf('day');
          break;
        case 'this_month':
          startDate = today.clone().startOf('month');
          endDate = today.clone().endOf('day');
          break;
        case 'last_month':
          startDate = today.clone().subtract(1, 'month').startOf('month');
          endDate = today.clone().subtract(1, 'month').endOf('month');
          break;
        default:
          startDate = today.clone().subtract(30, 'days').startOf('day');
          endDate = today.clone().endOf('day');
      }

      // IMPORTANT: Set date pickers with explicit format and log for debugging
      const startDateStr = startDate.format('YYYY-MM-DD');
      const endDateStr = endDate.format('YYYY-MM-DD');

      console.log('Setting date range:', { range, startDateStr, endDateStr });

      StartDatePicker.setValue(startDateStr);
      EndDatePicker.setValue(endDateStr);

      // Small delay to ensure date pickers update before refreshing
      setTimeout(() => {
        this.refreshCurrentReport();
      }, 100);
    },

    // Enhanced summary statistics calculation
    calculateSummaryStats: (data, reportType) => {
      if (!data || data.length === 0) return { isEmpty: true };

      switch(reportType) {
        case 'all_orders':
          const deliveredCount = data.filter(o =>
            o.status_display === 'Delivered' ||
            o.payment_status?.includes('Collected') ||
            o.payment_status?.includes('Already Paid')
          ).length;

          const cancelledCount = data.filter(o =>
            o.status_display === 'Cancelled'
          ).length;

          const pendingCount = data.filter(o =>
            o.status_display === 'Pending'
          ).length;

          const inTransitCount = data.filter(o =>
            o.status_display === 'In Transit'
          ).length;

          return {
            totalOrders: data.length,
            deliveredOrders: deliveredCount,
            cancelledOrders: cancelledCount,
            pendingOrders: pendingCount,
            inTransitOrders: inTransitCount,
            totalRevenue: data.reduce((sum, o) => sum + (o.order_amount_numeric || 0), 0),
            deliveryRate: data.length > 0 ? ((deliveredCount / data.length) * 100).toFixed(1) : 0,
            cancellationRate: data.length > 0 ? ((cancelledCount / data.length) * 100).toFixed(1) : 0
          };

        case 'daily_cash_flow':
          return {
            totalDays: data.length,
            totalOrders: data.reduce((sum, d) => sum + (d.total_orders || 0), 0),
            totalRevenue: data.reduce((sum, d) => sum + (d.total_revenue || 0), 0),
            avgOrdersPerDay: data.length > 0 ? (data.reduce((sum, d) => sum + (d.total_orders || 0), 0) / data.length).toFixed(1) : 0,
            avgRevenuePerDay: data.length > 0 ? (data.reduce((sum, d) => sum + (d.total_revenue || 0), 0) / data.length).toFixed(2) : 0
          };

        case 'payment_analysis':
          return {
            paymentMethods: data.length,
            totalOrders: data.reduce((sum, p) => sum + (p.total_orders || 0), 0),
            totalRevenue: data.reduce((sum, p) => sum + (p.total_revenue || 0), 0),
            avgSuccessRate: data.length > 0 ? (data.reduce((sum, p) => sum + (p.delivery_success_rate || 0), 0) /
  data.length).toFixed(1) : 0,
            codOrders: data.find(p => p.payment_method === 'COD')?.total_orders || 0,
            paidOrders: data.find(p => p.payment_method === 'Paid')?.total_orders || 0
          };

        case 'service_billing':
          return {
            totalServices: data.length,
            totalRevenue: data.reduce((sum, s) => sum + (s.total_amount || 0), 0),
            totalOrders: data.reduce((sum, s) => sum + (s.order_count || 0), 0),
            avgOrderValue: data.length > 0 ? (data.reduce((sum, s) => sum + (s.total_amount || 0), 0) / data.reduce((sum, s) => sum +
  (s.order_count || 0), 0)).toFixed(2) : 0
          };

        default:
          return { totalRecords: data.length };
      }
    },

    // Export report data (future enhancement)
    exportReport: (reportType, format = 'csv') => {
      // This can be enhanced to export reports in different formats
      showAlert(`Export ${reportType} as ${format} - Feature coming soon!`, 'info');
    }
  }