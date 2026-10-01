export class ActivityClock {
  constructor(time) { this.last=time; this.interaction=time; this.activeMs=0; }
  touch(time) { this.interaction=time; }
  step(time, eligible) {
    const elapsed=Math.max(0,Math.min(time-this.last,1500));
    if (eligible && time-this.interaction<300000) this.activeMs+=elapsed;
    this.last=time;
    return Math.floor(this.activeMs);
  }
}
