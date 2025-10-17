import { Card, CardContent, CardHeader } from '~/components/ui/card';
import { Skeleton } from '~/components/ui/skeleton';

/**
 * Loading skeleton component for content that is being fetched
 * Shows animated placeholders in the shape of article content
 */
export default function Loading() {
  return (
    <main className="max-w-3xl mx-auto px-4 py-12 flex-grow">
      <Card>
        <CardHeader className="space-y-4">
          {/* Category + Date */}
          <div className="flex items-center gap-4">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-28" />
          </div>

          {/* Title */}
          <Skeleton className="h-8 w-3/4" />
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Image placeholder */}
          <Skeleton className="w-full aspect-video rounded-md" />

          {/* Content placeholders */}
          <div className="space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />
          </div>
        </CardContent>
      </Card>
    </main>
  );
}