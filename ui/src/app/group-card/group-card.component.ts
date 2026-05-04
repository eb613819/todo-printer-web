import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-group-card',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './group-card.component.html',
  styleUrl: './group-card.component.scss'
})
export class GroupCardComponent {
  @Input() groupName = '';
  @Input() tasks: string[] = [];

  @Output() addTasks = new EventEmitter<string[]>();
  @Output() removeTask = new EventEmitter<number>();
  @Output() removeGroup = new EventEmitter<void>();
  @Output() printGroup = new EventEmitter<void>();

  newTaskInput = '';

  onAddTasks() {
    const tasks = this.newTaskInput.split(',').map(t => t.trim()).filter(Boolean);
    if (tasks.length) {
      this.addTasks.emit(tasks);
      this.newTaskInput = '';
    }
  }

  onKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') this.onAddTasks();
  }
}
