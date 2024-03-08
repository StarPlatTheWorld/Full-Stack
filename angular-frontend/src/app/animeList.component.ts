import { Component } from '@angular/core';
import { WebService } from './web.service';
import { HttpClient } from '@angular/common/http';
import { NavigationExtras } from '@angular/router';

@Component({
  selector: 'animeList',
  templateUrl: './animeList.component.html',
  styleUrls: ['./animeList.component.css']
})
export class AnimeListComponent {
    anime_list: any = [];
    page: number = 1;

    constructor(public webService: WebService) { }

    ngOnInit() {
      if (sessionStorage['page']) {
        this.page = Number(sessionStorage['page']);
      }
      this.anime_list = this.webService.getAnimeList(this.page);
    }

    previousPage() {
      if (this.page > 1) {
        this.page = this.page - 1;
        sessionStorage['page'] = this.page;
        this.anime_list = this.webService.getAnimeList(this.page);
      }
    }

    nextPage() {
      this.page = this.page + 1;
      sessionStorage['page'] = this.page;
      this.anime_list = this.webService.getAnimeList(this.page)
    }

}

