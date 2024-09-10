import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {map, Observable} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class BlogService {
  private contentFolder = 'assets/posts/';
  public blogPosts: Observable<IPostsEntity[]>;

  constructor(private http: HttpClient) {
    this.blogPosts = this.getBlogContent('posts.info.json', 'assets/')
      .pipe(
        map((data: string) => {
          return JSON.parse(data);
        }
      )
      )
  }

  getBlogPosts(): Observable<IPostsEntity[]>{
    return this.blogPosts;
  }

  getBlogContent(fileName: string, folder = this.contentFolder): Observable<string> {
    return this.http.get(`${folder}${fileName}`, { responseType: 'text' });
  }
}
export interface IPostsEntity {
  id: number;
  title: string;
  fileName: string;
  date: string;
}
