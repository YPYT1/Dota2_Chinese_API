import { EventIcon } from '@/components/icons';

export default function GameEventsPage() {
  return (
    <div className="flex flex-col items-center justify-center h-[50vh] text-center">
      <h1 className="text-2xl font-semibold tracking-tight">Game Events</h1>
      <p className="mt-2 text-muted-foreground max-w-md">
        Select an event from the sidebar to view its details.
      </p>
      <div className="mt-8 opacity-50">
        <div className="flex flex-col items-center gap-2">
          <div className="p-3 bg-muted rounded-lg">
            <EventIcon className="w-6 h-6" />
          </div>
          <span className="text-xs">Events</span>
        </div>
      </div>
    </div>
  );
}
