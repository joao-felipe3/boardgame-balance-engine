try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from src.btg import Role, InternProfile, simulate_single_match


def benchmark_profiles(n_per_profile: int = 10000):
    print("=" * 80)
    print(f" BENCHMARK COMPARATIVO DE PERFIS ({n_per_profile:,} PARTIDAS CADA) ")
    print("=" * 80)

    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]
    for prof in profiles:
        results = []
        for i in range(n_per_profile):
            res = simulate_single_match(i, prof, seed=500000 + i)
            results.append(res)
        df = pd.DataFrame(results)
        iw = (df["winner"] == Role.INTERN.value).sum()
        bw = (df["winner"] == Role.BANKER.value).sum()
        df["score"] = df["b_score"].astype(str) + " x " + df["i_score"].astype(str)
        climax = ((df["score"].isin(["4 x 3", "3 x 4"])).sum() / n_per_profile) * 100
        print(f"\n> {prof.value}")
        print(f"   - WR Estagiarios : {(iw/n_per_profile)*100:5.2f}%")
        print(f"   - WR Banqueiros  : {(bw/n_per_profile)*100:5.2f}%")
        print(f"   - Duracao Media  : {df['rounds'].mean():.2f} rodadas")
        print(f"   - Climax 7a Roda : {climax:5.2f}%")
    print("=" * 80)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", "-n", type=int, default=10000)
    args = parser.parse_args()
    benchmark_profiles(args.games)
