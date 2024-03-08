import { Component } from '@angular/core';
import { WebService } from './web.service';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'anime',
  templateUrl: './anime.component.html',
  styleUrls: ['./anime.component.css']
})
export class AnimeComponent {
    reviewForm: any;

    constructor(public webService: WebService,
                private route: ActivatedRoute,
                private formBuilder: FormBuilder) { }

    ngOnInit() {
        this.reviewForm = this.formBuilder.group({
          username: ['', Validators.required],
          review: ['', Validators.required],
          stars: 5
        });
        this.anime_list = this.webService.getAnime(this.route.snapshot.params['id']);
        this.reviews = this.webService.getReviews(this.route.snapshot.params['id']);
    }

    onSubmit() {
      this.webService.postReview(this.reviewForm.value).subscribe((response: any) => {
          this.reviewForm.reset();
          this.reviews = this.webService.getReviews(
                              this.route.snapshot.params['id']
          );
        });
    }

    isInvalid(control: any) {
      return this.reviewForm.controls[control].invalid &&
             this.reviewForm.controls[control].touched;
    }

    isUntouched() {
      return this.reviewForm.controls.username.pristine ||
             this.reviewForm.controls.review.pristine;
    }

    isIncomplete() {
      return this.isInvalid('username') ||
             this.isInvalid('review') ||
             this.isUntouched();
    }
    
    anime_list : any = [];

    reviews: any = [];

}