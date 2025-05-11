import { Component } from '@angular/core';
import { MessagesTopbarComponent } from '../TopBar/messages-topbar/messages-topbar.component';
import { SidebarComponent } from "../sidebar/sidebar.component";
@Component({
  selector: 'app-messages',
  standalone: true,
  imports: [MessagesTopbarComponent, SidebarComponent],
  templateUrl: './messages.component.html',
  styleUrl: './messages.component.css'
})
export class MessagesComponent {

}
