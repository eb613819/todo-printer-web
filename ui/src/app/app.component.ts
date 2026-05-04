import { Component, OnInit } from '@angular/core';
import { TasksService, TaskGroup } from './tasks.service';
import { HttpClientModule } from '@angular/common/http';
import { GroupCardComponent } from './group-card/group-card.component';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, GroupCardComponent, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  tasks: TaskGroup = {};
  showNewGroup = false;

  borderString = '';

  constructor(private tasksSvc: TasksService) {}

  ngOnInit() {
    this.generateBorder();
    window.addEventListener('resize', () => this.generateBorder());
    this.tasksSvc.getTasks().subscribe(data => {
      this.tasks = data;
    });
  }

  generateBorder() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;
    ctx.font = '0.8rem Courier Prime';
    const charWidth = ctx.measureText('*').width;
    const count = Math.floor(window.innerWidth / charWidth);
    this.borderString = '*'.repeat(count);
  }

  printAll() {
    this.tasksSvc.printGroups(Object.keys(this.tasks)).subscribe();
  }

  groupNames(): string[] {
    return Object.keys(this.tasks);
  }

  onAddTasks(group: string, newTasks: string[]) {
    this.tasksSvc.addTasks(group, newTasks).subscribe(data => this.tasks = data);
  }

  onRemoveTask(group: string, index: number) {
    this.tasksSvc.removeTask(group, index).subscribe(data => this.tasks = data);
  }

  onRemoveGroup(group: string) {
    this.tasksSvc.removeGroup(group).subscribe(data => this.tasks = data);
  }

  onPrintGroup(group: string) {
    this.tasksSvc.printGroups([group]).subscribe();
  }

  newGroupName = '';
  newGroupTasks = '';

  createGroup() {
    const name = this.newGroupName.trim();
    const tasks = this.newGroupTasks.split(',').map(t => t.trim()).filter(Boolean);
    if (!name) return;
    this.tasksSvc.addGroup(name, tasks).subscribe(data => {
      this.tasks = data;
      this.newGroupName = '';
      this.newGroupTasks = '';
      this.showNewGroup = false;
    });
  }
}
