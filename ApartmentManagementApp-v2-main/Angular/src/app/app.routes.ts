import { Route } from '@angular/router';

export const routes: Route[] = [
  { path: '', redirectTo: 'home-page', pathMatch: 'full' },

  // ================= PUBLIC PAGES =================
  {
    path: 'home-page',
    loadComponent: () =>
      import('./Components/home-page/home-page.component').then(m => m.HomePageComponent)
  },
  {
    path: 'apartment/:id',
    loadComponent: () =>
      import('./Components/apartment-details/apartment-details.component').then(m => m.ApartmentDetailsComponent)
  },
  {
    path: 'buy-homes',
    loadComponent: () =>
      import('./Components/buy-homes/buy-homes.component').then(m => m.BuyHomesComponent)
  },
  {
    path: 'rent-homes',
    loadComponent: () =>
      import('./Components/rent-homes/rent-homes.component').then(m => m.RentHomesComponent)
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./Components/LoginPage/login/login.component').then(m => m.LoginComponent)
  },

  // ================= MAINTENANCE CENTER =================
  {
    path: 'maintenance-center/:userId',
    loadComponent: () =>
      import('./Components/maintenance-center/maintenance-center.component').then(
        m => m.MaintenanceCenterComponent
      )
  },

  // ================= DASHBOARDS =================
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./Components/dashboard/dashboard.component').then(m => m.DashboardComponent),
    children: [
      { path: '', redirectTo: 'technician-requests', pathMatch: 'full' },
      {
        path: 'technician-requests',
        loadComponent: () =>
          import('./Components/technician-requests/technician-requests.component').then(
            m => m.TechnicianRequestsComponent
          )
      }
    ]
  },

  // ================= TECHNICIAN DASHBOARD =================
  {
    path: 'technician-dashboard',
    loadComponent: () =>
      import('./Components/technician-dashboard/technician-dashboard.component').then(
        m => m.TechnicianDashboardComponent
      ),
    children: [
      { path: '', redirectTo: 'assignments', pathMatch: 'full' },
      {
        path: 'assignments',
        loadComponent: () =>
          import('./Components/technician-assignments/technician-assignments.component').then(
            m => m.TechnicianAssignmentsComponent
          )
      },
      {
        path: 'assignment-details/:id',
        loadComponent: () =>
          import('./Components/technician-assignment-details/technician-assignment-details.component').then(
            m => m.TechnicianAssignmentDetailsComponent
          )
      },
      {
        path: 'requests',
        loadComponent: () =>
          import('./Components/technician-requests/technician-requests.component').then(
            m => m.TechnicianRequestsComponent
          )
      },
      {
        path: 'maintenance-request/:id',
        loadComponent: () =>
          import('./Components/maintenance-request-detail/maintenance-request-detail.component').then(
            m => m.MaintenanceRequestDetailComponent
          )
      }
    ]
  },

  // ================= TENANT DASHBOARD =================
  {
    path: 'tenant-dashboard',
    loadComponent: () =>
      import('./Components/tenant-dashboard/tenant-dashboard.component').then(
        m => m.TenantDashboardComponent
      ),
    children: [
      { path: '', redirectTo: 'maintenance-center', pathMatch: 'full' },
      {
        path: 'maintenance-center',
        loadComponent: () =>
          import('./Components/maintenance-center/maintenance-center.component').then(
            m => m.MaintenanceCenterComponent
          )
      },
      {
        path: 'maintenance-request',
        loadComponent: () =>
          import('./Components/maintenance-request/maintenance-request.component').then(
            m => m.MaintenanceRequestComponent
          )
      },
      {
        path: 'maintenance-request/:id',
        loadComponent: () =>
          import('./Components/maintenance-request-detail/maintenance-request-detail.component').then(
            m => m.MaintenanceRequestDetailComponent
          ),
        data: { from: 'tenant' }
      }
    ]
  },

  // ================= OWNER DASHBOARD =================
  {
    path: 'owner-dashboard',
    loadComponent: () =>
      import('./Components/owner-dashboard/owner-dashboard.component').then(
        m => m.OwnerDashboardComponent
      ),
    children: [
      { path: '', redirectTo: 'maintenance-requests', pathMatch: 'full' },
      {
        path: 'maintenance-requests',
        loadComponent: () =>
          import('./Components/technician-requests/technician-requests.component').then(
            m => m.TechnicianRequestsComponent
          )
      },
      {
        path: 'maintenance-request/:id',
        loadComponent: () =>
          import('./Components/maintenance-request-detail/maintenance-request-detail.component').then(
            m => m.MaintenanceRequestDetailComponent
          ),
        data: { from: 'owner' }
      }
    ]
  },

  // ================= STANDALONE PAGES =================
  {
    path: 'maintenance-request',
    loadComponent: () =>
      import('./Components/maintenance-request/maintenance-request.component').then(
        m => m.MaintenanceRequestComponent
      )
  },
  {
    path: 'maintenance-request/:id',
    loadComponent: () =>
      import('./Components/maintenance-request-detail/maintenance-request-detail.component').then(
        m => m.MaintenanceRequestDetailComponent
      )
  },

  // ================= TECHNICIAN ROUTES =================
  {
    path: 'technician/:id',
    children: [
      { path: '', redirectTo: 'assignments', pathMatch: 'full' },
      {
        path: 'assignments',
        loadComponent: () =>
          import('./Components/technician-assignments/technician-assignments.component').then(
            m => m.TechnicianAssignmentsComponent
          )
      },
      {
        path: 'assignment-details/:requestId',
        loadComponent: () =>
          import('./Components/technician-assignment-details/technician-assignment-details.component').then(
            m => m.TechnicianAssignmentDetailsComponent
          )
      },
      {
        path: 'requests',
        loadComponent: () =>
          import('./Components/technician-requests/technician-requests.component').then(
            m => m.TechnicianRequestsComponent
          )
      }
    ]
  },

  // ================= FALLBACK =================
  { path: '**', redirectTo: 'home-page' }
];