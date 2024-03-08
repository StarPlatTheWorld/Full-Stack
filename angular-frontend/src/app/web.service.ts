import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { AuthService } from "@auth0/auth0-angular";
@Injectable()
export class WebService {

    private animeID: any;

    constructor(public http: HttpClient,
                private authService: AuthService) { }

    getAnimeList(page: number) {
        return this.http.get('http://localhost:5000/api/anime?pn=' + page);
    }

    getAnime(id: any) {
        this.animeID = id;
        return this.http.get('http://localhost:5000/api/anime/' + id)
    }

    getReviews(id: any) {
        return this.http.get('http://localhost:5000/api/anime/' + id + '/reviews')
    }

    postReview(review: any) {
        let postData = new FormData();
        postData.append("username", review.username);
        postData.append("review", review.review);
        postData.append("stars", review.stars);

        let today = new Date();
        let todayDate = today.getFullYear() + "-" +
                        today.getMonth() + "-" +
                        today.getDate();
        postData.append("date", todayDate);

        return this.http.post('http://localhost:5000/api/anime/' + this.animeID + '/reviews', postData);
    }
}