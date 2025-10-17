import { Card, CardContent, CardHeader } from '~/components/ui/card';
import { Skeleton } from '~/components/ui/skeleton';

/**
 * Loading skeleton component for content that is being fetched
 * Shows animated placeholders in the shape of article content
 */
export default function Loading() {
  return (
    <main className="max-w-3xl mx-auto px-4 py-12 flex-grow">
      <Card className="card-elevated relative overflow-hidden">
        {/* Gradient accent line */}
        <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary via-primary/60 to-transparent" />

        <CardHeader className="space-y-4 pt-6">
          {/* Emoji + Category + Date */}
          <div className="flex items-center gap-4">
            <Skeleton className="h-20 w-20 rounded-xl shimmer" />
            <div className="flex-1 space-y-3">
              <div className="flex items-center gap-2">
                <Skeleton className="h-6 w-24 rounded-full shimmer" />
                <Skeleton className="h-6 w-32 rounded-full shimmer" />
              </div>
              {/* Title */}
              <Skeleton className="h-8 w-full shimmer" />
              <Skeleton className="h-8 w-3/4 shimmer" />
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Summary box */}
          <div className="p-4 border-l-4 border-primary/20 bg-accent/50 rounded-r-lg space-y-2">
            <Skeleton className="h-4 w-full shimmer" />
            <Skeleton className="h-4 w-5/6 shimmer" />
          </div>

          {/* Content placeholders */}
          <div className="space-y-3">
            <Skeleton className="h-4 w-full shimmer" />
            <Skeleton className="h-4 w-full shimmer" />
            <Skeleton className="h-4 w-5/6 shimmer" />
            <Skeleton className="h-4 w-full shimmer" />
            <Skeleton className="h-4 w-3/4 shimmer" />
            <Skeleton className="h-4 w-full shimmer" />
            <Skeleton className="h-4 w-5/6 shimmer" />
            <Skeleton className="h-4 w-full shimmer" />
            <Skeleton className="h-4 w-2/3 shimmer" />
          </div>

          {/* Source section skeleton */}
          <div className="pt-6 border-t space-y-4">
            <div className="flex items-center gap-3">
              <Skeleton className="h-10 w-10 rounded-lg shimmer" />
              <Skeleton className="h-6 w-32 shimmer" />
            </div>
            <div className="space-y-3">
              {[...Array(2)].map((_, i) => (
                <div key={i} className="flex gap-4 p-4 border rounded-lg">
                  <Skeleton className="h-14 w-14 rounded-lg shimmer" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-full shimmer" />
                    <Skeleton className="h-3 w-2/3 shimmer" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}