// src/components/News/ArticleCard.js
import React from 'react';
import Image from 'next/image';
import Link from 'next/link';

function ArticleCard({ item }) {
  return (
    <article key={item.id} className="bg-white rounded-lg shadow overflow-hidden flex flex-col">
      <div className="relative w-full h-48">
        { item.image_url && (<Image
          src={item.image_url}
          alt={item.title}
          layout="fill"
          objectFit="cover"
        />)}
      </div>
      <div className="p-4 flex flex-col flex-grow">
        <h2 className="text-xl font-bold text-gray-800 mb-2">{item.title}</h2>
        <p className="text-gray-600 mb-3 line-clamp-3 flex-grow">{item.summary}</p>
        <div className="flex justify-between items-center mt-2">
          <span className="text-sm text-gray-500">{item.date}</span>
          <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded">
            {item.topic_name}
          </span>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {item.tags.slice(0, 3).map(tag => (
            <span key={tag.id} className="text-xs bg-gray-100 px-2 py-1 rounded">
              {tag.text}
            </span>
          ))}
        </div>
        <Link
          href={`/article/${item.id}`} // Assuming you have dynamic routes like /article/[id].js
          className="mt-4 text-red-600 hover:text-red-800 text-sm font-medium block"
        >
          Přečíst článek →
        </Link>
      </div>
    </article>
  );
}

export default ArticleCard;