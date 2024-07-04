odoo.define('tk_gym_management.GymDashboard', function (require) {
    'use strict';
    const AbstractAction = require('web.AbstractAction');
    const ajax = require('web.ajax');
    const core = require('web.core');
    const rpc = require('web.rpc');
    const session = require('web.session')
    const web_client = require('web.web_client');
    const _t = core._t;
    const QWeb = core.qweb;
    var self = this;

    const ActionMenu = AbstractAction.extend({

        template: 'gymDashboard',

        events: {
            'click .member-stats': 'view_member_stats',
            'click .membership-stats': 'view_membership_stats',
            'click .equipment-stats': 'view_equipment_stats',
            'click .workout-stats': 'view_workout_stats',
            'click .exercise-stats': 'view_exercise_stats',
            'click .yoga-stats': 'view_yoga_stats',
        },
        renderElement: function (ev) {
            const self = this;
            $.when(this._super())
                .then(function (ev) {
                    rpc.query({
                        model: "memberships.member",
                        method: "get_gym_stats",
                    }).then(function (result) {
                        $('#gym_members').empty().append(result['gym_members']);
                        $('#gym_memberships').empty().append(result['gym_memberships']);
                        $('#gym_equipments').empty().append(result['gym_equipments']);
                        $('#gym_workouts').empty().append(result['gym_workouts']);
                        $('#gym_exercises').empty().append(result['gym_exercises']);
                        $('#gym_classes').empty().append(result['gym_classes']);
                        self.membershipcategories(result['get_membership'])
                        self.paymentMonth(result['invoice'])
                        self.attendancedate(result['daily_attendance'])
                        self.membershipperson(result['membershipperson'])
                    });
                });
        },
        view_member_stats : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Members'),
                type: 'ir.actions.act_window',
                res_model: 'res.partner',
                domain: [['is_member', '=', true]],
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_membership_stats : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Memberships'),
                type: 'ir.actions.act_window',
                res_model: 'memberships.member',
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },
        view_equipment_stats : function (ev){
            this.get_action(ev, 'Equipments', 'gym.equipment');
        },
        view_workout_stats : function (ev){
            this.get_action(ev, 'Workouts', 'gym.workout');
        },
        view_exercise_stats : function (ev){
            this.get_action(ev, 'Exercises', 'gym.exercise');
        },
        view_yoga_stats : function (ev){
             ev.preventDefault();
            return this.do_action({
                name: _t('Yoga Classes'),
                type: 'ir.actions.act_window',
                res_model: 'gym.class',
                views: [[false, 'list'],[false, 'form']],
                target: 'current'
            });
        },

        get_action: function (ev, name, res_model){
            ev.preventDefault();
            return this.do_action({
                name: _t(name),
                type: 'ir.actions.act_window',
                res_model: res_model,
                views: [[false, 'kanban'],[false, 'tree'],[false, 'form']],
                target: 'current'
            });
        },
          apexGraph: function () {
            Apex.grid = {
                padding: {
                    right: 0,
                    left: 0,
                    top: 10,
                }
            }
            Apex.dataLabels = {
                enabled: false
            }
        },

   attendancedate: function(data){
        const options = {
          series: [{
          name: 'Employees',
          data: data[1]
        }, {
          name: 'Members',
          data: data[2]
        }],
          chart: {
          type: 'bar',
          height: 350,
          stacked: true,
          toolbar: {
            show: true
          },
          zoom: {
            enabled: true
          }
        },
        responsive: [{
          breakpoint: 480,
          options: {
            legend: {
              position: 'bottom',
              offsetX: -10,
              offsetY: 0
            }
          }
        }],
        plotOptions: {
          bar: {
            horizontal: false,
            borderRadius: 10,
            dataLabels: {
              total: {
                enabled: true,
                style: {
                  fontSize: '13px',
                  fontWeight: 900
                }
              }
            }
          },
        },
        xaxis: {
         categories: data[0],
        },
        legend: {
          position: 'right',
          offsetY: 40
        },
        fill: {
          opacity: 1
        }
        };
         this.renderGraph("#attendance", options);
        },

      membershipcategories: function(data){
          const options = {
                series: data[1],
                chart: {
                    type: 'pie',
                    height: 410
                },
                colors: ['#F7A4A4', '#344D67', '#B6E2A1','#FEBE8C'],
                dataLabels: {
                    enabled: false
                },
                labels: data[0],
                legend: {
                    position: 'bottom',
                },
            };
              this.renderGraph("#membership_categories", options);
          },
      membershipperson: function(data){
       const options = {
          series: [{
          name: 'Male',
          data: data[1]
        }, {
          name: 'Female',
          data: data[2]
        }],
          chart: {
          type: 'bar',
          height: 350,
          stacked: true,
          toolbar: {
            show: true
          },
          zoom: {
            enabled: true
          }
        },
        responsive: [{
          breakpoint: 480,
          options: {
            legend: {
              position: 'bottom',
              offsetX: -10,
              offsetY: 0
            }
          }
        }],
        plotOptions: {
          bar: {
            horizontal: false,
            borderRadius: 10,
            dataLabels: {
              total: {
                enabled: true,
                style: {
                  fontSize: '13px',
                  fontWeight: 900
                }
              }
            }
          },
        },
        xaxis: {
         categories: data[0],
        },
        legend: {
          position: 'right',
          offsetY: 40
        },
        fill: {
          opacity: 1
        }
        };
      this.renderGraph("#membership_person", options);
      },

      paymentMonth: function(data){
       const options = {
          series: [
          {
            name: "Total Payment",
              data: data[1]
          }
        ],
          chart: {
          height: 350,

          toolbar: {
            show: false
          }
        },
        colors: ['#77B6EA', '#545454'],
        dataLabels: {
          enabled: false,
        },

        title: {
          text: '',
          align: 'left'
        },
        grid: {

          row: {
            colors: ['#f3f3f3'],
            opacity: 0.5
          },
        },
        markers: {
          size: 1
        },
        xaxis: {
           categories: data[0],
          title: {
            text: 'Month'
          }
        },
        yaxis: {
          title: {
            text: ''
          },
        },
        legend: {
          position: 'top',
          horizontalAlign: 'right',
        }
        };
         this.renderGraph("#payment_month", options);
        },

         renderGraph: function(render_id, options){
            $(render_id).empty();
            const graphData = new ApexCharts(document.querySelector(render_id), options);
            graphData.render();
        },

        willStart: function () {
       const self = this;
            return this._super()
            .then(function() {});
        },
    });
    core.action_registry.add('gym_dashboard', ActionMenu);

});
