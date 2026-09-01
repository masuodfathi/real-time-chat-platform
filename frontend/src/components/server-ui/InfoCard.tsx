interface InfoCardProps {
  title: string;
  description: string;
  rating?: number;
}

function InfoCard({
  title,
  description,
  rating,
}: InfoCardProps) {
  return (
    <div className="info-card">
      <h3>{title}</h3>

      {rating !== undefined && (
        <p>⭐ {rating}</p>
      )}

      <p>{description}</p>

      <button type="button">
        View Details
      </button>
    </div>
  );
}

export default InfoCard;