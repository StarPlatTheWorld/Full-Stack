import { Component } from '@angular/core';
import { MatGridListModule } from '@angular/material/grid-list';
import { AuthService } from '@auth0/auth0-angular';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  constructor(public authService: AuthService,
              public router: Router) { }
  title = 'AnimeDirect';
}
