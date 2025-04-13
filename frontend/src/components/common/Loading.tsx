/**
 * Loading skeleton component for content that is being fetched
 * Shows animated placeholders in the shape of article content
 */
export default function Loading() {
  return (
    <main className="max-w-3xl mx-auto px-4 py-12 flex-grow">
      <div className="animate-pulse">
        {/* Category + Date */}
        <div className="flex mb-4">
          <div className="h-5 w-16 bg-gray-200 rounded mr-4"></div>
          <div className="h-5 w-24 bg-gray-200 rounded"></div>
        </div>
        
        {/* Title */}
        <div className="h-10 w-3/4 bg-gray-200 rounded mb-6"></div>
        
        {/* Image placeholder */}
        <div className="w-full aspect-video bg-gray-200 rounded mb-8"></div>
        
        {/* Content placeholders */}
        <div className="space-y-4">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    </main>
  );
}