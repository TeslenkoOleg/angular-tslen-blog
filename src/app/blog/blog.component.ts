import { Component } from '@angular/core';
import {BlogService, IPostsEntity} from './blog.service';
import {Observable} from "rxjs";

@Component({
  selector: 'app-blog-list',
  templateUrl: './blog.component.html',
})
export class BlogComponent {
  blogPosts: Observable<IPostsEntity[]>;
  blogContent: string = '';

  constructor(private blogService: BlogService) {
    this.blogPosts = this.blogService.getBlogPosts();
  }

  loadPost(post: IPostsEntity['fileName']): void {
    this.blogService.getBlogContent(post).subscribe((content: string) => {
      this.blogContent = content;
    });
  }
}
