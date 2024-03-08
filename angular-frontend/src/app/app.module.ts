import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { AnimeListComponent } from './animeList.component';
import { HomeComponent } from './home.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { WebService } from './web.service';
import { HttpClientModule } from '@angular/common/http';
import { AnimeComponent } from './anime.component';
import { Router, RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { AuthModule } from '@auth0/auth0-angular';
import { NavComponent } from './nav.component';
import { AuthGuard } from '@auth0/auth0-angular';
import { FormsModule } from '@angular/forms';

var routes: any = [
  {
    path: '',
    component: HomeComponent
  },
  {
    path: 'anime',
    component: AnimeListComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'anime/:id',
    component: AnimeComponent,
    canActivate: [AuthGuard]
  },
  {
    path: '**',
    redirectTo: ''
  }
];

@NgModule({
  declarations: [
    AppComponent, AnimeListComponent, HomeComponent, AnimeComponent, NavComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
    ReactiveFormsModule,
    FormsModule,
    AuthModule.forRoot({
      domain: 'dev-d1zglhvx0fh44i2n.us.auth0.com',
      clientId: 'dAdbXIxIgp7wThua7ByaCwM4Tht1eCKz'
    })
  ],
  providers: [WebService],
  bootstrap: [AppComponent]
})
export class AppModule { }
