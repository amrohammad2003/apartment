import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-maintenance-center',
  templateUrl: './maintenance-center.component.html',
  styleUrls: ['./maintenance-center.component.css']
})
export class MaintenanceCenterComponent implements OnInit {
  userId: number | null = null;

  constructor(private route: ActivatedRoute, private router: Router) {}

  ngOnInit(): void {
    // Get userId from route parameter
    this.userId = parseInt(this.route.snapshot.paramMap.get('userId') || '0', 10);
    if (this.userId) {
      // Optionally, you can programmatically navigate after this
      this.router.navigate([`/maintenance-request-list`, this.userId]);
    }
  }
}
