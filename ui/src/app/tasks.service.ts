import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface TaskGroup {
  [groupName: string]: string[];
}

@Injectable({
  providedIn: 'root'
})
export class TasksService {
  private api = '/api';

  constructor(private http: HttpClient) {}

  getTasks(): Observable<TaskGroup> {
    return this.http.get<TaskGroup>(`${this.api}/tasks`);
  }

  addGroup(name: string, tasks: string[]): Observable<TaskGroup> {
    return this.http.post<TaskGroup>(`${this.api}/groups`, { name, tasks });
  }

  addTasks(group: string, tasks: string[]): Observable<TaskGroup> {
    return this.http.post<TaskGroup>(`${this.api}/groups/${group}/tasks`, { tasks });
  }

  removeTask(group: string, index: number): Observable<TaskGroup> {
    return this.http.delete<TaskGroup>(`${this.api}/groups/${group}/tasks/${index}`);
  }

  removeGroup(group: string): Observable<TaskGroup> {
    return this.http.delete<TaskGroup>(`${this.api}/groups/${group}`);
  }

  printGroups(groups: string[]): Observable<{ ok: boolean }> {
    return this.http.post<{ ok: boolean }>(`${this.api}/print`, { groups });
  }
}

