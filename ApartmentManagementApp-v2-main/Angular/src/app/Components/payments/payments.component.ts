import { Component } from '@angular/core';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { PaymentsTopbarComponent } from '../TopBar/payments-topbar/payments-topbar.component';
@Component({
  selector: 'app-payments',
  standalone: true,
  imports: [SidebarComponent,PaymentsTopbarComponent],
  templateUrl: './payments.component.html',
  styleUrl: './payments.component.css'
})
export class PaymentsComponent {

}
